"""
dataone.py

Functions related to querying the DataOne v1 API.
"""

import os
import urllib
import urllib2
import base64
import re
import xml.etree.ElementTree as ET

try:
    import RDF
except ImportError:
    import sys
    sys.path.append('/usr/lib/python2.7/dist-packages/')

import RDF


from d1lod import util


def getNumResults(query):
    """
    Performs a query and extracts just the number of results in the query.
    """

    num_results = -1

    xmldoc = util.getXML(query)
    result_node = xmldoc.findall(".//result")

    if result_node is not None:
        num_results = result_node[0].get('numFound')

    return int(num_results)


def createSinceQueryURL(from_string, to_string, fields=None, start=0, page_size=1000):
    """
    Creates a query string to get documents uploaded since `from_string` up
    to `to_string`.

    Parameters:

        from_string|to_string:
            String of form '2015-05-30T23:21:15.567Z'

        fields: optional
            List of string field names

        start|page_size: optional
            Solr query parameters
    """

    # Create the URL
    base_url = "https://cn.dataone.org/cn/v1/query/solr/"

    # Create a set of fields to grab
    if fields is None:
        fields = ",".join(getDefaultSolrIndexFields())
    else:
        fields = ",".join(fields)

    query_params = "formatType:METADATA+AND+(datasource:*LTER+OR+datasource:*"\
                   "KNB+OR+datasource:*PISCO+OR+datasource:*GOA)+AND+-"\
                   "obsoletedBy:*"

    query_params += "+AND+dateModified:[" +\
                    from_string +\
                    "%20TO%20" +\
                    to_string +\
                    "]"

    rows = page_size
    start = start

    query_string = "%s?fl=%s&q=%s&rows=%s&start=%s" % (base_url,
                                                       fields,
                                                       query_params,
                                                       rows,
                                                       start)

    return query_string


def getDocumentIdentifiersSince(from_string, to_string, fields=None, page_size=1000):
    """
    Get document identifiers for documents uploaded since `since`

    Parameters:
        from_string|to_string:
            String of form '2015-05-30T23:21:15.567Z'
    """

    # Get the number of pages we need
    query_string = createSinceQuery(from_string, to_string, fields, page_size)
    num_results = getNumResults(query_string)

    # Calculate the number of pages we need to get to get all results
    num_pages = num_results / page_size
    if num_results % page_size > 0:
        num_pages += 1

    print "Found %d documents over %d pages." % (num_results, num_pages)
    # util.continue_or_quit()

    # Collect the identifiers
    identifiers = []

    for page in range(1, num_pages + 1):
        page_identifiers = getIdentifiers(from_string, to_string, page)
        identifiers += page_identifiers

    return identifiers


def getSincePage(from_string, to_string, page=1, page_size=1000, fields=None):
    """
    Get a page off the Solr index for a query between two time periods.
    """

    start = (page-1) * page_size
    query_string = createSinceQueryURL(from_string, to_string, start=start, page_size=page_size)
    query_xml = util.getXML(query_string)

    return query_xml


def getIdentifiersSince(from_string, to_string, fields=None, page=1, page_size=1000):
    """
    Query page `page` of the Solr index using and retrieve the PIDs
    of the documents in the response.
    """
    start = (page-1) * page_size
    query_string = createSinceQuery(from_string, to_string, fields, start)

    query_xml = util.getXML(query_string)

    identifiers = query_xml.findall(".//str[@name='identifier']")

    if identifiers is None:
        return []

    identifier_strings = []

    for identifier in identifiers:
        if identifier.text is not None:
            print identifier.text
            identifier_strings.append(identifier.text)

    return identifier_strings


def getSystemMetadata(identifier, cache=True):
    """
    Gets the system metadata for an identifier.

    In development, I'm keeping a cache of documents in the root of the
    d1lod folder at ./cache. This will need to be removed in
    production. This is toggled with the argument `cache`.

    Arguments:
        identifier: str
            PID of the document
        cache: bool
            Whether to cache files in the current working directory

    Returns:
        An XML document
    """

    sysmeta = None

    # Try from cache first
    if cache is True:
        print "Attempting to get scimeta from local cache for...%s" % identifier

        if not os.path.exists("./cache"):
            os.mkdir("./cache")

        if not os.path.exists("./cache/meta"):
            os.mkdir("./cache/meta")

        cache_filename = base64.urlsafe_b64encode(identifier)
        cache_filepath = './cache/meta/' + cache_filename

        if os.path.isfile(cache_filepath):
            print "  Loading from cache."

            sysmeta = ET.parse(cache_filepath)

    if sysmeta is not None:
        return sysmeta

    query_string = "https://cn.dataone.org/cn/v1/meta/%s" % identifier
    sysmeta = util.getXML(query_string)

    # Cache what we found for next time
    if sysmeta is not None and cache is True:
        with open(cache_filepath, "wb") as f:
            f.write(ET.tostring(sysmeta))

    return sysmeta


def getScientificMetadata(identifier, identifier_map={}, cache=True):
    """
    Gets the scientific metadata for an identifier.
    Optionally, loads the file from a cache which is a dump of documents with
    filenames like 'autogen...' (which need to be mapped to a PID).

    In development, I'm keeping a cache of documents in the root of the
    d1lod folder at ./cache. This will need to be removed in
    production. This is toggled with the argument `cache`.

    Arguments:
        identifier: str
            PID of the document

        identifier_map: Dict
            An identifier<->filename mapping

        cache_dir: str
            The base directory path to the cache

        cache: bool
            Whether to cache files in the current working directory

    Returns:
        An XML document
    """

    scimeta = None

    # Try from cache first
    if cache is True:
        print "Attempting to get scimeta from local cache for...%s" % identifier

        if not os.path.exists("./cache"):
            os.mkdir("./cache")

        if not os.path.exists("./cache/object/"):
            os.mkdir("./cache/object")

        cache_filename = base64.urlsafe_b64encode(identifier)
        cache_filepath = './cache/object/' + cache_filename

        print "  Looking for filename %s" % cache_filename

        if os.path.isfile(cache_filepath):
            print "  Loading from cache."

            scimeta = ET.parse(cache_filepath)

            if scimeta is not None:
                scimeta = scimeta.getroot()

    # Return cached copy if we successfully got it
    if scimeta is not None:
        return scimeta

    if identifier in identifier_map:
        mapped_filename = identifier_map[identifier]
        mapped_file_path = cache_dir + mapped_filename

        if os.path.isfile(mapped_file_path):
            scimeta = ET.parse(mapped_file_path).getroot()

    if scimeta is None:
        query_string = "https://cn.dataone.org/cn/v1/object/%s" % urllib.quote_plus(identifier)
        scimeta = util.getXML(query_string)

    # Cache what we found for next time
    if scimeta is not None and cache is True:
        with open(cache_filepath, "wb") as f:
            f.write(ET.tostring(scimeta))

    return scimeta


def extractDocumentIdentifier(doc):
    """
    Get an identifier from an XML document.

    doc can either be a sysmeta or a Solr index result

    We try to use it as if it was a Solr index element
    then fall back to trying it as a sysmeta record
    """

    identifier = None

    if doc.find(".//str[@name='identifier']") is not None:
        identifier = doc.find(".//str[@name='identifier']").text
    elif doc.find(".//identifier") is not None:
        identifier = doc.find(".//identifier").text

    if identifier is None:
        raise Exception("Failed to add dataset because the identifier couldn't be processed.")

    return identifier


def getSolrIndexFields(identifier, fields=None):
    """
    Gets a single document off the Solr index by searching for its identifier.
    """

    # Replace everything, up to and including, the last : in the string
    # Solr can't handle colons, even escaped

    last_colon = identifier.rfind(":")

    if last_colon != -1:
        identifier = "*" + identifier[last_colon+1:]

    identifier_esc = urllib.quote_plus(identifier)

    if fields is None:
        fields = getDefaultSolrIndexFields()

    query_string = "http://cn.dataone.org/cn/v1/query/solr/?fl=" + ",".join(fields) + "&q=id:" + identifier_esc + "&rows=1&start=0"
    query_xml = util.getXML(query_string)

    return query_xml.find(".//doc")


def getAggregatedIdentifiers(identifier):
    """
    Retrieves and parses the resource map with the specified identifier.

    Returns: List(str)
        List of identifiers.

    """

    if type(identifier) is not str or len(identifier) < 1:
        raise Exception("Bad identifier string passed to method.")

    model = RDF.Model()
    parser = RDF.Parser(name="rdfxml")
    #
    base_url = "https://cn.dataone.org/cn/v1/object/"
    query_url = base_url + identifier
    #
    try:
        parser.parse_into_model(model, query_url)
    except RDF.RedlandError as e:
        print "Exception: Failed to parse RDF/XML at `%s`: %s" % (query_url, e)

    query = """
    SELECT ?s ?o
    WHERE {
        ?s <http://www.openarchives.org/ore/terms/aggregates> ?o
    }
    """

    q = RDF.Query(query)

    identifiers = []

    for result in q.execute(model):
        if 'o' not in result:
            continue

        object_node = result['o']

        if object_node.is_resource():
            object_node_str = str(object_node)
            identifier = extractIdentifierFromFullURL(object_node_str)

            if identifier is not None:
                identifiers.append(identifier)

    return identifiers


def extractIdentifierFromFullURL(url):
    """Extracts just the PID from a full URL.
    Handles URLs on v1 or v2 and meta/object/resolve/etc endpoints.

    Arguments:
        url : str

    Returns: None if no match. Otherwise returns the identifier as a string.
    """

    if not isinstance(url, str):
        return None
        
    url_regex = r"https://cn.dataone.org/cn/v\d/\w+/(.*)"
    search = re.search(url_regex, url)

    if search is None:
        return None

    return search.group(1)


def getDefaultSolrIndexFields():
    return ["identifier","title","abstract","author",
        "authorLastName", "origin","submitter","rightsHolder","documents",
        "resourceMap","authoritativeMN","obsoletes","northBoundCoord",
        "eastBoundCoord","southBoundCoord","westBoundCoord","beginDate","endDate",
        "datasource","replicaMN","resourceMap","dataUrl"]
