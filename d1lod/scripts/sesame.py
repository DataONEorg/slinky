import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))

import logging
logging.basicConfig(level=logging.DEBUG)

from d1lod import dataone, validator, util, jobs
from d1lod.people import processing
from d1lod.sesame import Store, Repository, Interface

if __name__ == '__main__':

    logging.info("Main routine started.")

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

    s = Store("localhost", 8080)
    r = Repository(s, "d1lod", namespaces)
    i = Interface(r)

    i.addDataset('knb-lter-bes.462.56')

    sys.exit()

    from_string =   "2015-12-29T00:00:00.0Z"
    to_string   =   jobs.getNowString()
    print from_string
    print to_string


    query_string = dataone.createSinceQueryURL(from_string, to_string, None, 0)
    num_results = dataone.getNumResults(query_string)
    print num_results

    page_size=1000
    num_pages = num_results / page_size

    if num_results % page_size > 0:
        num_pages += 1

    # Process each page
    for page in range(1, num_pages + 1):
        page_xml = dataone.getSincePage(from_string, to_string, page, page_size)
        docs = page_xml.findall(".//doc")

        for doc in docs:
            identifier = dataone.extractDocumentIdentifier(doc)
            i.addDataset(identifier, doc)

    # identifier = 'doi:10.6073/AA/knb-lter-arc.376.1'
    # jobs.add_dataset(identifier)

    # jobs.updateVoIDFile('test')
    # jobs.setLastRun()
