import os
import pytest
import xml.etree.ElementTree as ET
import d1_common
import RDF

from d1lod.legacy.graph import Graph
from d1lod.legacy.interface import Interface
from d1lod.client import SlinkyClient


@pytest.fixture
def client():
    return SlinkyClient()


@pytest.fixture(scope="module")
def store():
    return Graph("localhost", 8890, "test")


@pytest.fixture(scope="module")
def graph(store):
    namespaces = {
        "owl": "http://www.w3.org/2002/07/owl#",
        "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "xsd": "http://www.w3.org/2001/XMLSchema#",
        "foaf": "http://xmlns.com/foaf/0.1/",
        "dcterms": "http://purl.org/dc/terms/",
        "datacite": "http://purl.org/spar/datacite/",
        "geolink": "http://schema.geolink.org/1.0/base/main#",
        "d1dataset": "http://dataone.org/dataset/",
        "d1person": "http://dataone.org/person/",
        "d1org": "http://dataone.org/organization/",
        "d1node": "https://cn.dataone.org/cn/v1/node/",
        "d1landing": "https://search.dataone.org/#view/",
        "prov": "http://www.w3.org/ns/prov#",
    }

    graphh = Graph("localhost", 8890, "test", ns=namespaces)

    return graphh


@pytest.fixture(scope="module")
def interface(graph):
    return Interface()


@pytest.fixture
def model():
    storage = RDF.MemoryStorage()
    model = RDF.Model(storage=storage)

    return model


def load_xml_to_str(relpath):
    filestring = None

    with open(os.path.join("tests/data/", relpath), "rb") as f:
        filestring = f.read()

    return filestring


def load_xml(relpath):
    filestring = None

    with open(os.path.join("tests/data/", relpath), "rb") as f:
        filestring = f.read()

    return ET.fromstring(filestring)


def load_sysmeta(path):
    return d1_common.types.dataoneTypes.CreateFromDocument(
        load_xml_to_str(os.path.join("sysmeta", path))
    )


def load_metadata(path):
    return load_xml(os.path.join("metadata", path))


def print_model(model):
    serializer = RDF.TurtleSerializer()
    print(serializer.serialize_model_to_string(model))
