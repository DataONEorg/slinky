import pytest


@pytest.mark.integration
def test_that_store_query_works(sparql_store):
    response = sparql_store.query("select ?s ?p ?o where { ?s ?p ?o } limit 1")

    assert len(response) >= 0


@pytest.mark.integration
def test_that_store_insert_model_works(sparql_store, test_model):
    response = sparql_store.insert_model(test_model)

    assert (
        str(response[0]["callret-0"])
        == "Insert into <https://dataone.org>, 1 (or less) triples -- done"
    )


@pytest.mark.integration
def test_can_handle__inserts(sparql_store, large_model):
    response = sparql_store.insert_model(large_model)

    assert (
        str(response[0]["callret-0"])
        == "Insert into <https://dataone.org>, 1000 (or less) triples -- done"
    )
