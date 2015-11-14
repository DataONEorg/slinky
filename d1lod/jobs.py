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

from d1lod.sesame import store
from d1lod.sesame import repository
from d1lod.sesame import interface

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
    'd1landing': 'https://search.dataone.org/#view/'
}

SESAME_HOST = os.getenv('GRAPHDB_PORT_8080_TCP_ADDR', 'localhost')
SESAME_PORT = os.getenv('GRAPHDB_PORT_8080_TCP_PORT', '8080')
SESAME_REPOSITORY = 'test'
REDIS_LAST_RUN_KEY = "lastrun"

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


    t = getNowString()

    conn.set(redis_last_run_key, t)
def update_graph():
    """
    Job that updates the entire graph.

    Datasets that have been added to the DataOne network since the last run will
    be added to the triple store.
    """
    JOB_NAME = "JOB_UPDATE"
    print "[%s] Job started" % JOB_NAME

    s = store.SesameStore(SESAME_HOST, SESAME_PORT)
    r = repository.SesameRepository(s, SESAME_REPOSITORY, namespaces)
    i = interface.SesameInterface(r)

    from_string = getLastRun()

    if from_string is None:
        setLastRun()
        return

    to_string = getNowString()
    # DEBUG
    from_string = "2015-11-05T00:00:00.0Z"
    #DEBUG
    query_string = dataone.createSinceQueryURL(from_string, to_string, None, 0)
    print query_string
    num_results = dataone.getNumResults(query_string)
    print num_results

    # Calculate the number of pages we need to get to get all results
    page_size=1000
    num_pages = num_results / page_size

    if num_results % page_size > 0:
        num_pages += 1

    # Process each page
    for page in range(1, num_pages + 1):
        page_xml = dataone.getSincePage(from_string, to_string, page, page_size)
        docs = page_xml.findall(".//doc")

        for doc in docs:
            i.addDataset(doc)

    setLastRun()

def one_off_job():
    s = store.SesameStore(SESAME_HOST, SESAME_PORT)
    r = repository.SesameRepository(s, SESAME_REPOSITORY, namespaces)
    i = interface.SesameInterface(r)

    identifier = 'doi:10.6085/AA/YB15XX_015MU12004R00_20080619.50.1'
    doc = dataone.getSolrIndexFields(identifier)
    i.addDataset(doc)


if __name__ == '__main__':
    hourly_job()
