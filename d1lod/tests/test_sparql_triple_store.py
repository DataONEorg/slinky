import pytest
import RDF

from d1lod.client import SlinkyClient
from d1lod.stores.sparql_triple_store import SparqlTripleStore

client = SlinkyClient(store=SparqlTripleStore)

# TODO: Move to a fixture?
def create_test_model():
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


# TODO: Move to a fixture?
def create_dummy_model(size=100):
    storage = RDF.MemoryStorage()
    model = RDF.Model(storage=storage)

    for i in range(size):
        model.add_statement(
            RDF.Statement(
                RDF.Node(RDF.Uri(f"http://example.com/subject{i}")),
                RDF.Node(RDF.Uri(f"http://example.com/predicate{i}")),
                RDF.Node(str(i)),
            )
        )

    return model


def test_that_store_query_works():
    response = client.store.query("select ?s ?p ?o where { ?s ?p ?o } limit 1")

    assert len(response) == 1


def test_that_store_insert_model_works():
    model = create_test_model()
    response = client.store.insert_model(model)

    assert response == ""


def test_can_handle_big_inserts():
    model = create_dummy_model(5000)

    s = RDF.NTriplesSerializer()
    print(s.serialize_model_to_string(model))

    assert len(model) == 5000

    response = client.store.insert_model(model)
    assert response["modified"] == 5000
    assert response["milliseconds"] >= 0
