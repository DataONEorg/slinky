import sys
import os
import logging
logging.basicConfig(level=logging.DEBUG)

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))

from d1lod import (jobs, dataone)
from d1lod.sesame import (Store, Repository, Interface)

if __name__ == '__main__':
    s = Store("virtuoso", 8890)
    r = Repository("virtuoso", 8890, 'geolink')
    i = Interface(r)

    ###########
    r.clear()
    i.addDataset('sschen.7.1')
    i.addDataset('sschen.7.2')
    # jobs.add_dataset(r, i, identifier, doc)

    ###########

    # identifier = 'doi:10.6085/AA/YB15XX_015MU12004R00_20080619.50.1'
    # doc = dataone.getSolrIndexFields(identifier)
    # i.addDataset(doc)

    ###########
    #
    # from_string = "2015-12-30T00:00:00.0Z"
    # to_string = jobs.getNowString()
    #
    # query_string = dataone.createSinceQueryURL(from_string, to_string, None, 0)
    # print query_string
    #
    # num_results = dataone.getNumResults(query_string)
    # print num_results
    #
    # page = 1
    # page_size = 10
    # num_pages = num_results / page_size
    #
    # page_xml = dataone.getSincePage(from_string, to_string, page=page, page_size=page_size)
    # documents = page_xml.findall(".//doc")
    #
    # for document in documents:
    #     identifier = dataone.extractDocumentIdentifier(document)
    #     print identifier
    #     i.addDataset(identifier, document)


    #########
    # Test delete perf
    # r.clear()
    # r.import_from_file('/Users/mecum/Desktop/d1lod.ttl', fmt='turtle', context='d1lod')
    # print r.size()
    #
    # r.delete_triples_about('?s', context='d1lod')

    # print r.namespaces()
