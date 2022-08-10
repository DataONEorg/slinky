import pytest
import RDF


@pytest.mark.integration
def test_that_store_query_works(virtuoso_store):
    response = virtuoso_store.query("select ?s ?p ?o where { ?s ?p ?o } limit 1")

    assert len(response) >= 0


@pytest.mark.integration
def test_that_store_insert_model_works(virtuoso_store, test_model):
    virtuoso_store.clear()
    assert virtuoso_store.count() == 0

    response = virtuoso_store.insert_model(test_model)

    assert response
    assert virtuoso_store.count() > 0


@pytest.mark.integration
def test_can_handle__large_inserts(virtuoso_store, large_model):
    virtuoso_store.clear()
    assert virtuoso_store.count() == 0

    response = virtuoso_store.insert_model(large_model)

    assert response
    assert virtuoso_store.count() == 1000


@pytest.mark.integration
def test_can_handle_huge_inserts(virtuoso_store, huge_model):
    virtuoso_store.clear()
    assert virtuoso_store.count() == 0

    response = virtuoso_store.insert_model(huge_model)

    assert response
    assert virtuoso_store.count() == 5000


@pytest.mark.integration
def test_if_we_insert_a_statement_we_can_query_it(virtuoso_store):
    virtuoso_store.clear()

    # First confirm it's not already there
    response = virtuoso_store.query(
        'select * where { <http://example.com/subject> <http://example.com/predicate> "my object" . }'
    )

    assert len(response) == 0

    # Do insert
    stmt = RDF.Statement(
        RDF.Node(RDF.Uri("http://example.com/subject")),
        RDF.Node(RDF.Uri("http://example.com/predicate")),
        RDF.Node(literal="my object"),
    )
    virtuoso_store.insert_statement(stmt)

    # Verify
    second_response = virtuoso_store.query(
        'select count(*) where { <http://example.com/subject> <http://example.com/predicate> "my object" . }'
    )

    assert len(second_response) == 1
    assert int(str(second_response[0]["callret-0"])) == 1


@pytest.mark.integration
def test_we_can_delete_statements(virtuoso_store):
    virtuoso_store.clear()

    assert virtuoso_store.count() == 0

    stmt = RDF.Statement(
        RDF.Node(RDF.Uri("http://example.com/subject")),
        RDF.Node(RDF.Uri("http://example.com/predicate")),
        RDF.Node(literal="my object"),
    )

    virtuoso_store.insert_statement(stmt)

    pattern = '<http://example.com/subject> <http://example.com/predicate> "my object"'

    response = virtuoso_store.count(pattern)
    assert response == 1

    response = virtuoso_store.delete(pattern)
    assert response == 1

    response = virtuoso_store.count(pattern)
    assert response == 0


@pytest.mark.integration
def test_we_can_delete_statements_by_wildcard(virtuoso_store):
    virtuoso_store.clear()

    assert virtuoso_store.count() == 0

    stmt = RDF.Statement(
        RDF.Node(RDF.Uri("http://example.com/subject")),
        RDF.Node(RDF.Uri("http://example.com/predicateA")),
        RDF.Node(literal="my object"),
    )

    virtuoso_store.insert_statement(stmt)

    stmt = RDF.Statement(
        RDF.Node(RDF.Uri("http://example.com/subject")),
        RDF.Node(RDF.Uri("http://example.com/predicateB")),
        RDF.Node(literal="my object"),
    )

    virtuoso_store.insert_statement(stmt)

    stmt = RDF.Statement(
        RDF.Node(RDF.Uri("http://example.com/subject")),
        RDF.Node(RDF.Uri("http://example.com/predicateC")),
        RDF.Node(literal="my object"),
    )

    virtuoso_store.insert_statement(stmt)

    pattern = "<http://example.com/subject> ?p ?o"

    response = virtuoso_store.count(pattern)
    assert response == 3

    response = virtuoso_store.delete(pattern)
    assert response == 3

    response = virtuoso_store.count(pattern)
    assert response == 0
