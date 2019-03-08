"""
Process a dataset (by PID) for dataset/people/org triples.
"""


import os
import sys
import datetime
import json
import uuid
import pandas
import xml.etree.ElementTree as ET
import urllib

# Append parent dir so we can keep these scripts in /scripts
sys.path.insert(1, os.path.join(sys.path[0], '../'))

from d1lod import settings
from d1lod import dataone
from d1lod import util
from d1lod import validator
from d1lod import store
from d1lod import multi_store

from d1lod.people import processing

from d1lod.people.formats import eml
from d1lod.people.formats import dryad
from d1lod.people.formats import fgdc


if __name__ == "__main__":
    identifier = 'doi:10.6085/AA/YB15XX_015MU12004R00_20080619.50.1'
    cache_dir = "/Users/mecum/src/d1dump/documents/"
    formats_map = util.loadFormatsMap()

    namespaces = {
        "foaf": "http://xmlns.com/foaf/0.1/",
        "dcterms": "http://purl.org/dc/terms/",
        "datacite": "http://purl.org/spar/datacite/",
        "owl": "http://www.w3.org/2002/07/owl#",
        "xsd": "http://www.w3.org/2001/XMLSchema#",
        "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "glview": "http://schema.geolink.org/dev/view/",
        "d1people": "https://dataone.org/person/",
        "d1org": "https://dataone.org/organization/",
        "d1resolve": "https://cn.dataone.org/cn/v1/resolve/",
        "prov": "http://www.w3.org/ns/prov#",
        "d1node": "https://cn.dataone.org/cn/v1/node/",
        "d1landing": "https://search.dataone.org/#view/",
        "d1repo": "https://cn.dataone.org/cn/v1/node/"
    }

    # Load triple stores
    stores = {
        'people': graph.Graph("http://virtuoso/", "8890" , 'geolink', namespaces),
        'organizations': graph.Graph("http://virtuoso/", "8890",  'geolink', namespaces),
        'datasets': graph.Graph("http://virtuoso/", "8890", 'geolink', namespaces)
    }

    stores = multi_store.MultiStore(stores, namespaces)
    stores.clear()


    # Establish which fields we want to get from the Solr index
    fields = ["identifier","title","abstract","author",
    "authorLastName", "origin","submitter","rightsHolder","documents",
    "resourceMap","authoritativeMN","obsoletes","northBoundCoord",
    "eastBoundCoord","southBoundCoord","westBoundCoord","startDate","endDate",
    "datasource","replicaMN","resourceMap"]

    vld = validator.Validator()

    scimeta = dataone.getScientificMetadata(identifier, cache=True)
    doc = dataone.getSolrIndex(identifier, fields)
    records = processing.extractCreators(identifier, scimeta)

    print records

    # Add records and organizations
    people = [p for p in records if 'type' in p and p['type'] == 'person']
    organizations = [o for o in records if 'type' in o and o['type'] == 'organization']

    # Always do organizations first, so peoples' organization URIs exist
    for organization in organizations:
        organization = vld.validate(organization)
        stores.addOrganization(organization)

    for person in people:
        person = vld.validate(person)
        stores.addPerson(person)

    stores.addDataset(doc, scimeta, formats_map)

    stores.save()
