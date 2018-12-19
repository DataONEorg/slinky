"""d1lod.virtuoso.repository

This is a utility module for the d1lod service to read and write d1lod contents
to the Virtuoso repositories. It contains the following functionality:

1. Insertion of some triples, given inline in the request, into a repository
2. Deletion of some triples, given inline in the request, if the respective repository contains those
3. Loading of the contents of a document representing a repository into a repository
4. Clearing of all the triples in (one or more) repositories.
5. Conditional Insert / delete of d1lod contents
6. Retreiving contents of a repository

"""

import requests
import RDF
import json
import logging
import xml.etree.ElementTree as ET


class Repository:
    def __init__(self, host, port, name, ns={}):
        self.name = name
        self.ns = ns
        self.host = host
        self.port = port
        self.endpoints = {
            'sparql': 'http://%s:%s/sparql' % (self.host, self.port),
        }

        # Set aside a Session object
        # We use this when making HTTP requests to reduce overhead when making
        # many requests during the lifetime of a Repository objects
        self.session = requests.Session()


    def __str__(self):
        return "Repository: '%s'" % self.name


    def exists(self, repository_name):
        """Execute a SPARQL QUERY against the Repository.

        Arguments:
        ----------

        None


        Returns: A boolean value representing the existence of the Repository."""
        query_string = "ASK WHERE { GRAPH <" + repository_name + "> { ?s ?p ?o } }"
        sparqlResponse = self.query(query_string=query_string, accept='text/plain')
        return sparqlResponse.content


    def insert(self, s, p, o, context=None):
        """Insert a triple using a SPARQL UPDATE query.

        Arguments:
        ----------
        s : (RDF.Node / RDF.Uri, str
        p : (RDF.Node / RDF.Uri, str
        o : (RDF.Node / RDF.Uri, str

        context : str
            (optional) Name of the context to execute the query against
        """

        # checks if the payload contains a blank node or not
        blank_node = self.tripleHasBlankNode(s, p, o)

        subj_string = self.term_to_sparql(s)
        pred_string = self.term_to_sparql(p)
        obj_string = self.term_to_sparql(o)
        payload_string= subj_string + " " + pred_string + " " + obj_string

        return(self.insert_data(repository_name="geolink", payload=payload_string, blank_node = blank_node))



    def insert_data(self, repository_name = None, payload='', prefix='', blank_node = False):
        """The INSERT DATA operation adds some triples, given inline in the request, into a repository.
        This should create the destination repository if it does not exist. If the repository does not exist
        and it can not be created for any reason, then a failure must be returned.

        Arguments:
        ----------

        repository_name: str
            the <URI> of the repository

        payload: str
            contents / triples to be loaded in the string

        prefix: str
            prefixes used


        Returns: None."""
        if repository_name is None:
            repository_name = self.name
        insert_query = "INSERT \n{\n\tGRAPH <" + repository_name + ">\n\t{\n\t\t" + payload + "\n\t}" + "\n}"

        return(self.query(query_string=insert_query, blank_node = blank_node))


    def delete_data(self, repository_name, payload='', prefix='', blank_node = False):
        """The DELETE DATA operation adds some triples, given inline in the request, into a repository.
        This should create the destination repository if it does not exist. If the repository does not exist
        and it can not be created for any reason, then a failure must be returned.

        Arguments:
        ----------

        repository_name: str
            the <URI> of the repository

        payload: str
            contents / triples to be loaded in the string

        prefix: str
            prefixes used


        Returns: None."""
        delete_query ="DELETE \n{\n\tGRAPH <" + repository_name + ">\n\t{\n\t\t" + payload + "\n\t}" + "\n}"
        sparqlResponse = self.query(query_string=delete_query, blank_node = blank_node)
        return(sparqlResponse)


    def namespacePrefixString(self):
        """Generate a string of namespaces suitable for appending to the front
        of a SPARQL QUERY, i.e.,

            @prefix x: <http://x.com> .
            @prefix y: <http://y.com> .

        Returns: (str) Newline-separated @prefix: <x> . string.
        """

        ns = self.ns

        ns_strings = []

        for key in ns:
            ns_strings.append("PREFIX %s:<%s>" % (key, ns[key]))

        return "\n".join(ns_strings)


    def query(self, query_string, blank_node = False, accept='application/json'):
        """Execute a SPARQL QUERY against the Repository.

        Arguments:
        ----------

        query_string : str
            SPARQL query string.

        accept : str
            An appropriate HTTP Accept header value. Defaults to JSON.

        formatResponse: boolean
            A boolean value indicating the formatting requirements of the results.


        Returns: A result dict containing the query response."""

        # getrting the namespaces before performing the query
        prefix = self.namespacePrefixString()

        results = {}
        endpoint = self.endpoints['sparql']
        if(blank_node):
            where_clause = """
            WHERE {
                SELECT * {
                    OPTIONAL { ?s ?p ?o . }
                } LIMIT 1
            }
             """
            query_string + where_clause
        params = {
            'query': prefix+"\n"+query_string
        }

        print(params["query"])


        r = self.session.post(endpoint, params=params, auth=('dba', 'dev.nceas'))
        print(r)
        print r.headers

        results = None

        if r.status_code != 200:
            logging.error("SPARQL QUERY failed. Status was not 200 as expected.")
            logging.error(r.status_code)
            logging.error(r.text)
            logging.error(query_string)
        else:
            response_type = "xml"
            response_var = r.content
            results = self.processResponse(response_var)

        return results


    def term_to_sparql(self, term):
        """Convert an RDF term to a suitable string to be inserted into a
        SPARQL query.
        """

        if isinstance(term, str):
            # Do nothing to bindings
            if term.startswith('?'):
                return term
            else:
                return "%s" % term
        elif isinstance(term, RDF.Node):
            if term.is_resource():
                return "<%s>" % str(term)
            else:
                return "%s" % str(term)
        elif isinstance(term, RDF.Uri):
            return "<%s>" % str(term)

    def update(self, query_string):
        """Execute a SPARQL UPDATE query against the repository.

        Arguments:
        ----------

        query_string : str
            SPARQL query string.
        """

        # getrting the namespaces before performing the query
        prefix = self.namespacePrefixString()
        
        query_string = prefix + "\n" + query_string
        
        endpoint = self.endpoints['sparql']

        r = self.session.post(endpoint, data={'update': query_string.strip()})

        if r.status_code != 204:
            print "SPARQL UPDATE failed. Status was not 204 as expected."
            print endpoint
            print r.text
            print query_string

        return r


    def etree_to_dict(self,t):
        return {t.tag: map(self.etree_to_dict, t.iterchildren()) or t.text}


    def processResponse(self, response_var):
        """Process a JSON response from the Repository and create a friendlier
        format. The format is a list of Dicts, where the names in each dict
        match the bindings of the query.
        """

        response_content = ET.fromstring(response_var)


        xml_result_element = []
        xml_results_element = None
        xml_result = []


        for child in response_content:
            if child.tag == '{http://www.w3.org/2005/sparql-results#}head':
                xml_head_element = child
            elif child.tag == '{http://www.w3.org/2005/sparql-results#}results':
                xml_results_element = child
            else:
                pass

        for child in xml_results_element:
            if child.tag == '{http://www.w3.org/2005/sparql-results#}result':
                xml_result_element.append(child)

        for result in xml_result_element:
            xml_result = []
            for binding in result:
                xml_result_dict = {}
                binding_key = binding.attrib["name"]
                binding_val = None
                for uri in binding:
                    binding_val = uri.text
                xml_result_dict[binding_key] = binding_val
                xml_result.append(xml_result_dict)

        return xml_result


    def tripleHasBlankNode(self, s , p , o):
        """

        s : RDF.Node | str
            The subject of the triple pattern.

        p : RDF.Node | str
            The predicate of the triple pattern.

        o : RDF.Node | str
            The object of the triple pattern.

        :return:
            A boolean value indicating whether either of the s / p / o is a blank node or not
        """

        # Check for blank nodes:
        if isinstance(s, RDF.Node):
            if s.is_blank():
                return True
        elif isinstance(s, str):
            if s.startswith("_:"):
                return True


        if isinstance(p, RDF.Node):
            if p.is_blank():
                return True
        elif isinstance(p, str):
            if p.startswith("_:"):
                return True

        if isinstance(o, RDF.Node):
            if o.is_blank():
                return True
        elif isinstance(o, str):
            if o.startswith("_:"):
                return True

        return  False


if __name__ == "__main__":
    repository1 = Repository("localhost", "8890", "geolink")

    query = """
        PREFIX foaf:<http://xmlns.com/foaf/0.1/>
        PREFIX owl:<http://www.w3.org/2002/07/owl#>
        PREFIX xsd:<http://www.w3.org/2001/XMLSchema#>
        PREFIX datacite:<http://purl.org/spar/datacite/>
        PREFIX d1node:<https://cn.dataone.org/cn/v1/node/>
        PREFIX d1dataset:<http://lod.dataone.org/dataset/>
        PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#>
        PREFIX prov:<http://www.w3.org/ns/prov#>
        PREFIX geolink:<http://schema.geolink.org/1.0/base/main#>
        PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX d1person:<http://lod.dataone.org/person/>
        PREFIX d1org:<http://lod.dataone.org/organization/>
        PREFIX dcterms:<http://purl.org/dc/terms/>
        SELECT (count(DISTINCT ?person)  as ?count) WHERE { ?person rdf:type geolink:Dataset }
    """

    # print(json.dumps(
    #     repository1.insert(s=RDF.Uri('http://www.w3.org/ns/prov#' + 'wasRevisionOf'), p=RDF.Uri('http://www.w3.org/2002/07/owl#' + 'inverseOf'),
    #                        o=RDF.Uri('http://www.w3.org/ns/prov#' + 'hadRevision')), indent=2))
    # print(json.dumps(repository1.insert(s='<http://www.w3.org/ns/prov#wasRevisionOf>', p='<http://www.w3.org/2002/07/owl#inverseOf>', o='<http://www.w3.org/ns/prov#hadRevision>'), indent=2))

    # repository1.insert_data("urn:sparql:tests:insert:data", payload=payload)

    print(repository1.query(query_string=query))