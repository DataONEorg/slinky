import pytest
import RDF

from d1lod.client import SlinkyClient

client = SlinkyClient()

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
                RDF.Node(RDF.Uri("http://example.com/subject")),
                RDF.Node(RDF.Uri("http://example.com/predicate")),
                RDF.Node(f"http://example.com/object{i}"),
            )
        )

    return model


def test_that_store_query_works():
    response = client.store.query("select ?s ?p ?o where { ?s ?p ?o } limit 1")

    assert len(response) == 1


def test_that_store_insert_model_works():
    model = create_test_model()
    response = client.store.insert_model(model)

    assert response["modified"] == 1
    assert response["milliseconds"] >= 0


def test_parse_mutation_response_works():
    ex = '<data modified="5" milliseconds="112" />'
    result = client.store.parse_mutation_result(ex)

    assert result["modified"] == 5
    assert result["milliseconds"] == 112


def test_can_handle_big_inserts():
    model = create_dummy_model(5000)
    assert len(model) == 5000

    response = client.store.insert_model(model)
    assert response["modified"] == 5000
    assert response["milliseconds"] >= 0