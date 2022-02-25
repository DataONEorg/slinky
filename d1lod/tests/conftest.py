import os
import pytest
import xml.etree.ElementTree as ET
import d1_common
import RDF

from d1lod.client import SlinkyClient
from d1lod.stores.local_store import LocalStore
from d1lod.stores.blazegraph_store import BlazegraphStore
from d1lod.stores.virtuoso_store import VirtuosoStore
from d1lod.stores.sparql_triple_store import SparqlTripleStore

from d1lod.settings import (
    REDIS_HOST,
    REDIS_PORT,
    GRAPH_HOST,
    GRAPH_PORT,
    BLAZEGRAPH_HOST,
    BLAZEGRAPH_PORT,
)


@pytest.fixture
def client():
    return SlinkyClient()


@pytest.fixture
def local_client():
    return SlinkyClient(store=LocalStore)


@pytest.fixture
def local_store():
    return LocalStore()


@pytest.fixture
def sparql_store():
    return SparqlTripleStore(endpoint=f"{GRAPH_HOST}:{GRAPH_PORT}/sparql")


@pytest.fixture
def blazegraph_store():
    return BlazegraphStore(f"{BLAZEGRAPH_HOST}:{BLAZEGRAPH_PORT}/bigdata")


@pytest.fixture
def virtuoso_store():
    return VirtuosoStore(endpoint=f"{GRAPH_HOST}:{GRAPH_PORT}")


@pytest.fixture
def model():
    storage = RDF.MemoryStorage()
    model = RDF.Model(storage=storage)

    return model


@pytest.fixture
def test_model():
    storage = RDF.MemoryStorage()
    model = RDF.Model(storage=storage)
    model.add_statement(
        RDF.Statement(
            RDF.Node(RDF.Uri("http://example.com/subject")),
            RDF.Node(RDF.Uri("http://example.com/predicate")),
            RDF.Node("http://example.com/object"),
        )
    )

    return model


@pytest.fixture
def small_model():
    return create_model_of_size(100)


@pytest.fixture
def medium_model():
    return create_model_of_size(500)


@pytest.fixture
def large_model():
    return create_model_of_size(1000)


@pytest.fixture
def huge_model():
    return create_model_of_size(5000)


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


def create_model_of_size(size=100):
    storage = RDF.MemoryStorage()
    model = RDF.Model(storage=storage)

    for i in range(size):
        model.add_statement(
            RDF.Statement(
                RDF.Node(RDF.Uri("http://example.com/subject")),
                RDF.Node(RDF.Uri("http://example.com/predicate")),
                RDF.Node(f"http://example.com/object{i}"),
            )
        )

    return model
