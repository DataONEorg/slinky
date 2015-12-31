import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))


from d1lod import dataone, validator, util, jobs
from d1lod.people import processing
from d1lod.sesame import Store, Repository, Interface

if __name__ == '__main__':

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
    r = Repository(s, "test", namespaces)
    i = Interface(r)

    ###########

    # identifier = 'knb-lter-bes.462.56'
    # i.addDataset(identifier)

    ###########

    # identifier = 'doi:10.6085/AA/YB15XX_015MU12004R00_20080619.50.1'
    # doc = dataone.getSolrIndexFields(identifier)
    # i.addDataset(doc)

    ###########

    from_string =   "2015-12-30T00:00:00.0Z"

    to_string   =   jobs.getNowString()

    query_string = dataone.createSinceQueryURL(from_string, to_string, None, 0)
    print query_string

    num_results = dataone.getNumResults(query_string)
    print num_results


    page_size=1000
    num_pages = num_results / page_size

    if num_results % page_size > 0:
        num_pages += 1

    for page in range(1, num_pages + 1):
        print "Processing page %d." % page

        page_xml = dataone.getSincePage(from_string, to_string, page=page, page_size=page_size)
        docs = page_xml.findall(".//doc")

        for doc in docs[0:4]:
            identifier = dataone.extractDocumentIdentifier(doc)
            print identifier
            i.addDataset(identifier, doc)
