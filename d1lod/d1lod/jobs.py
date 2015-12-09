""" jobs.py

A collection of common jobs for the D1 LOD service.
"""

import os
import sys
import uuid
import datetime
from redis import StrictRedis

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))

from d1lod import dataone

from d1lod.sesame import Store, Repository, Interface

conn = StrictRedis(host='redis', port='6379')

namespaces = {
    'owl': 'http://www.w3.org/2002/07/owl#',
    'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
    'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    'xsd': 'http://www.w3.org/2001/XMLSchema#',
    'foaf': 'http://xmlns.com/foaf/0.1/',
    'dcterms': 'http://purl.org/dc/terms/',
    'datacite': 'http://purl.org/spar/datacite/',
    'glbase': 'http://schema.geolink.org/',
    'd1dataset': 'http://lod.dataone.org/dataset/',
    'd1person': 'http://lod.dataone.org/person/',
    'd1org': 'http://lod.dataone.org/organization/',
    'd1node': 'https://cn.dataone.org/cn/v1/node/',
    'd1landing': 'https://search.dataone.org/#view/',
    "prov": "http://www.w3.org/ns/prov#"

}

SESAME_HOST = os.getenv('GRAPHDB_PORT_8080_TCP_ADDR', 'localhost')
SESAME_PORT = os.getenv('GRAPHDB_PORT_8080_TCP_PORT', '8080')
SESAME_REPOSITORY = 'd1lod'
REDIS_LAST_RUN_KEY = 'lastrun'

def getNowString():
    """
    Returns the current time in UTC as a string with the format of
    2015-01-01T12:34:56.789Z
    """

    t = datetime.datetime.utcnow()
    return t.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

def getLastRun():
    """
    Gets the time job was run
    """

    if not conn.exists(REDIS_LAST_RUN_KEY):
        return None
    else:
        return conn.get(REDIS_LAST_RUN_KEY)

def setLastRun(to=None):
    """
    Sets the last run timestamp
    """
    if to is None:
        to = getNowString()

    print "Setting lastrun: %s" % to
    conn.set(REDIS_LAST_RUN_KEY, to)

def calculate_stats():
    """
    Collect and print out statistics about the graph.
    """

    JOB_NAME = "JOB_GRAPH_STATS"
    print "[%s] Job started" % JOB_NAME

    s = Store(SESAME_HOST, SESAME_PORT)
    r = Repository(s, SESAME_REPOSITORY, namespaces)
    i = Interface(r)

    print "[%s] repository.size: %d" % (JOB_NAME, r.size())

def update_graph():
    """
    Job that updates the entire graph.

    Datasets that have been added to the DataOne network since the last run will
    be added to the triple store.
    """
    JOB_NAME = "JOB_UPDATE"
    print "[%s] Job started" % JOB_NAME

    s = Store(SESAME_HOST, SESAME_PORT)
    r = Repository(s, SESAME_REPOSITORY, namespaces)
    i = Interface(r)

    # Grab size before doing work
    before_size = r.size()

    from_string = getLastRun()

    if from_string is None:
        setLastRun()
        return

    to_string = getNowString()
    print "[%s] Hourly job running FROM:%s TO:%s" % (JOB_NAME, from_string, to_string)

    query_string = dataone.createSinceQueryURL(from_string, to_string, None, 0)

    num_results = dataone.getNumResults(query_string)
    print "[%s] num_results: %d" % (JOB_NAME, num_results)

    # Calculate the number of pages we need to get to get all results
    page_size=1000
    num_pages = num_results / page_size

    if num_results % page_size > 0:
        num_pages += 1

    print "[%s] num_pages: %d" % (JOB_NAME, num_pages)

    # Process each page
    for page in range(1, num_pages + 1):
        page_xml = dataone.getSincePage(from_string, to_string, page, page_size)
        docs = page_xml.findall(".//doc")

        for doc in docs:
            identifier = dataone.extractDocumentIdentifier(doc)
            print "[%s] addDataset: %s" % (JOB_NAME, identifier)

            i.addDataset(doc)

    setLastRun(to_string)

    # Grab size after doing work
    after_size = r.size()
    size_diff = after_size - before_size

    print "[%s] size_difference: %d" % (JOB_NAME, size_diff)


def export_graph():
    JOB_NAME = "EXPORT_GRAPH"
    print "[%s] Job started" % JOB_NAME

    s = Store(SESAME_HOST, SESAME_PORT)
    r = Repository(s, SESAME_REPOSITORY, namespaces)
    i = Interface(r)

    with open("/www/d1lod.ttl", "wb") as f:
        dump = r.export()
        f.write(dump)



if __name__ == '__main__':
    print "main executed"
