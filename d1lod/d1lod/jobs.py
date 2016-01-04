from __future__ import division

""" jobs.py

A collection of common jobs for the D1 LOD service.
"""

import os
import sys
import time
import uuid
import datetime
import math
import RDF
import logging

from redis import StrictRedis
from rq import Queue

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))

from d1lod import dataone
from d1lod.sesame import Store, Repository, Interface

conn = StrictRedis(host='redis', port='6379')
q = Queue(connection=conn)
QUEUE_MAX_SIZE = 1000 # Controls whether adding new jobs is delayed
QUEUE_MAX_SIZE_STANDOFF = 60 # (seconds) time to sleep before trying again

# Set up connections to services
SESAME_HOST = os.getenv('WEB_1_PORT_8080_TCP_ADDR', 'localhost')
SESAME_PORT = os.getenv('WEB_1_PORT_8080_TCP_PORT', '8080')
SESAME_REPOSITORY = 'd1lod'
REDIS_LAST_RUN_KEY = 'lastrun'

# Set up file paths
VOID_FILENAME = "void.ttl"
VOID_FILEPATH = "/www/" + VOID_FILENAME
DUMP_FILENAME = "d1lod.ttl"


def getNowString():
    """Returns the current time in UTC as a string with the format of
    2015-01-01T12:34:56.789Z
    """

    t = datetime.datetime.utcnow()
    return t.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def getLastRun():
    """Gets the time job was run"""

    if not conn.exists(REDIS_LAST_RUN_KEY):
        return None
    else:
        return conn.get(REDIS_LAST_RUN_KEY)


def setLastRun(to=None):
    """Sets the last run timestamp"""

    if to is None:
        """Set to a default value. Here, we manually set it to a date prior to
        the date the first document was uploaded, which can be found via the
        query:

        https://cn.dataone.org/cn/v1/query/solr/?fl=dateUploaded&q=formatType:METADATA&rows=1&start=0&sort=dateUploaded+asc
        """

        # to = "2000-01-01T00:00:00Z" # Default
        to = getNowString()

    # Validate the to string
    if not isinstance(to, str):
        logging.error("Value of 'to' parameter not a string. Value='%s'.", to)
        return

    if not len(to) > 0:
        logging.error("Value of 'to' parameter is zero-length. Value='%s'.", to)
        return

    logging.info("Setting Redis key '%s' to '%s'.", REDIS_LAST_RUN_KEY, to)
    conn.set(REDIS_LAST_RUN_KEY, to)


def createVoIDModel(to):
    """Creates an RDF Model according to the VoID Dataset spec for the given
    arguments.

    Returns: RDF.Model"""

    # Validate the to string
    if not isinstance(to, str):
        logging.error("Value of 'to' parameter not a string. Failed to update VoID file. Value=%s.", to)
        return None

    if not len(to) > 0:
        logging.error("Value of 'to' parameter is zero-length. Failed to update VoID file. Value=%s.", to)
        return None


    # Prepare the model
    m = RDF.Model(RDF.MemoryStorage())

    rdf = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'
    void = "http://rdfs.org/ns/void#"
    d1lod = "http://lod.dataone.org/"
    dcterms = "http://purl.org/dc/terms/"

    subject_node = RDF.Node(blank="d1lod")

    # Add in our statements
    m.append(RDF.Statement(subject_node,
                           RDF.Uri(rdf+'type'),
                           RDF.Uri(void+'Dataset')))

    m.append(RDF.Statement(subject_node,
                           RDF.Uri(void+'feature'),
                           RDF.Uri(d1lod+'fulldump')))

    m.append(RDF.Statement(subject_node,
                           RDF.Uri(dcterms+'modified'),
                           RDF.Node(to)))

    m.append(RDF.Statement(subject_node,
                           RDF.Uri(void+'dataDump'),
                           RDF.Uri(d1lod+DUMP_FILENAME)))

    return m


def updateVoIDFile(to):
    """Updates a VoID file with a new last-modified value.

    Note: The filepath of the VoID file is accessed by a global variable.

    The resulting VoID file should look something like this:

    @prefix void: <http://rdfs.org/ns/void#> .
    @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
    @prefix dcterms: <http://purl.org/dc/terms/> .
    @prefix d1lod: <http://lod.dataone.org/> .
    @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

    d1lod:d1lod a void:Dataset ;
      void:feature d1lod:fulldump ;
      dcterms:modified "2015-11-01";
      void:dataDump d1lod:d1lod.ttl .
    """

    # Create the VoID RDF Model
    m = createVoIDModel(to)


    # Verify the size of the model as a check for its successful creation
    if m.size() != 4:
        logging.error("The VoID model that was created was the wronng size (%d, not %d).", m.size(), 4)
        return


    # Create a serializer
    s = RDF.Serializer(name="turtle")


    # Add in namespaces
    void = "http://rdfs.org/ns/void#"
    d1lod = "http://lod.dataone.org/"

    s.set_namespace('rdf', namespaces['rdf'])
    s.set_namespace('void', void)
    s.set_namespace('dcterms', namespaces['dcterms'])
    s.set_namespace('d1lod', d1lod)


    # Write to different locations depending on production or testing
    try:
        if os.path.isfile(VOID_FILEPATH):
            s.serialize_model_to_file(VOID_FILEPATH, m)
        else:
            s.serialize_model_to_file('./void.ttl', m)
    except Exception, e:
        logging.exception(e)


def calculate_stats():
    """Collect and print out statistics about the graph.
    """

    JOB_NAME = "JOB_GRAPH_STATS"
    logging.info("[%s] Job started.", JOB_NAME)

    s = Store(SESAME_HOST, SESAME_PORT)
    r = Repository(s, SESAME_REPOSITORY, namespaces)

    logging.info("[%s] repository.size=%d", JOB_NAME, r.size())

    # Count Datasets, People, Organizations, etc
    concepts = [ 'glbase:Dataset', 'glbase:DigitalObject', 'glbase:Identifier',
                 'glbase:Person', 'glbase:Organization' ]

    concept_strings = []

    for concept in concepts:
        query = """SELECT (count(DISTINCT ?person)  as ?count)
            WHERE { ?person rdf:type %s }""" % concept

        result = r.query(query)

        if len(result) != 1 or 'count' not in result[0]:
            logging.info("Failed to get count for %s.", concept)
            continue

        concept_strings.append("%s:%s" % (concept, result[0]['count']))

    logging.info("[%s] Distinct Concepts: %s.", JOB_NAME, "; ".join(concept_strings))


def update_graph():
    """Job that updates the entire graph.

    Datasets that have been added to the DataOne network since the last run will
    be added to the triple store.
    """
    JOB_NAME = "JOB_UPDATE"
    logging.info("[%s] Job started.", JOB_NAME)

    """Determine the time period over which to get datasets.

    If the Redis database is fresh and does not have a value set for
    REDIS_LAST_RUN_KEY, we initialize the key with the datetime string that is
    earlier than the first uploaded dataset.
    """

    from_string = getLastRun()

    if from_string is None:
        setLastRun()

    from_string = getLastRun()
    to_string = getNowString()
    logging.info("[%s] Running update job: from_string=%s to_string=%s", JOB_NAME, from_string, to_string)

    # Create the Solr query to grab the datasets
    query_string = dataone.createSinceQueryURL(from_string, to_string, None, 0)

    num_results = dataone.getNumResults(query_string)
    logging.info("[%s] num_results=%d", JOB_NAME, num_results)

    # Calculate the number of pages we need to get to get all results
    page_size = 1000
    num_pages = int(math.ceil(num_results / page_size))

    logging.info("[%s] num_pages=%d", JOB_NAME, num_pages)

    # Set up Store/Repository/Interface once per update job
    # This ensures that all add_dataset jobs use the same instance of each
    # which reduces uncessary overhead

    store = Store(SESAME_HOST, SESAME_PORT)
    repository = Repository(store, SESAME_REPOSITORY, namespaces)
    interface = Interface(repository)

    # Enqueue each page
    for page in range(1, num_pages + 1):
        q.enqueue(add_page, repository, interface, from_string, to_string, page, page_size)

    logging.info("[%s] Done queueing datasets.", JOB_NAME)
    logging.info("[%s] Setting lastrun key to %s.", JOB_NAME, to_string)

    setLastRun(to_string)

    # Update the void file if we updated the graph
    if num_results > 0:
        logging.info("[%s] Updating VoID file located at VOID_FILEPATH='%s' with new modified value of to_string='%s'.", JOB_NAME, VOID_FILEPATH, to_string)
        updateVoIDFile(to_string)


def add_page(repository, interface, from_string, to_string, page, page_size):
    """Enqueues datasets on a given page of Solr results."""

    JOB_NAME = "JOB_ADD_PAGE"
    logging.info("[%s] Job started.", JOB_NAME)
    logging.info("[%s] Adding page='%s'", JOB_NAME, page)

    page_xml = dataone.getSincePage(from_string, to_string, page, page_size)
    docs = page_xml.findall(".//doc")

    for doc in docs:
        identifier = dataone.extractDocumentIdentifier(doc)

        # Sleep until the number of jobs in the queue goes down
        while len(q) > QUEUE_MAX_SIZE:
            time.sleep(QUEUE_MAX_SIZE_STANDOFF) # Seconds

        logging.info("[%s] Queueing job add_dataset with identifier='%s'", JOB_NAME, identifier)
        q.enqueue(add_dataset, repository, interface, identifier, doc)



def add_dataset(repository, interface, identifier, doc=None):
    """Adds the dataset from a set of Solr fields."""

    JOB_NAME = "JOB_ADD_DATASET"
    logging.info("[%s] [%s] Job started.", JOB_NAME, identifier)
    logging.info("[%s] [%s] Adding dataset with identifier='%s'", JOB_NAME, identifier, identifier)

    # Handle case where no Solr fields were passed in
    if doc is None:
        doc = dataone.getSolrIndexFields(identifier)

    if doc is None:
        raise Exception("No solr fields could be retrieved for dataset with PID %s.", identifier)

    # Collect stats for before and after
    datetime_before = datetime.datetime.now()
    size_before = repository.size()

    # Add the dataset
    interface.addDataset(doc)

    # Collect stats for after
    datetime_after = datetime.datetime.now()
    datetime_diff = datetime_after - datetime_before
    datetime_diff_seconds = datetime_diff.seconds + datetime_diff.microseconds / 1e6
    size_after = repository.size()
    size_diff = size_after - size_before
    statements_per_second = size_diff / datetime_diff_seconds

    logging.info("[%s] [%s] Repository size change: %d (%d -> %d).", JOB_NAME, identifier, size_diff, size_before, size_after)
    logging.info("[%s] [%s] Dataset added in: %f second(s).", JOB_NAME, identifier, datetime_diff_seconds)
    logging.info("[%s] [%s] Statements per second: %f second(s).", JOB_NAME, identifier, round(statements_per_second, 2))


def export_graph():
    JOB_NAME = "EXPORT_GRAPH"
    logging.info("[%s] Job started.", JOB_NAME)

    s = Store(SESAME_HOST, SESAME_PORT)
    r = Repository(s, SESAME_REPOSITORY, namespaces)

    logging.info("[%s] Exporting graph of size %d.", JOB_NAME, r.size())

    try:
        with open("/www/d1lod.ttl", "wb") as f:
            dump = r.export()
            f.write(dump.encode('utf-8'))
    except Exception, e:
        logging.exception(e)
