def test_that_store_query_works(blazegraph_store):
    response = blazegraph_store.query("select ?s ?p ?o where { ?s ?p ?o } limit 1")

    assert len(response) == 1


def test_that_store_insert_model_works(blazegraph_store, test_model):
    response = blazegraph_store.insert_model(test_model)

    assert response["modified"] == 1
    assert response["milliseconds"] >= 0


def test_parse_mutation_response_works(blazegraph_store):
    ex = '<data modified="5" milliseconds="112" />'
    result = blazegraph_store.parse_mutation_result(ex)

    assert result["modified"] == 5
    assert result["milliseconds"] == 112


def test_can_handle_big_inserts(blazegraph_store, huge_model):
    response = blazegraph_store.insert_model(huge_model)
    assert response["modified"] == 5000
    assert response["milliseconds"] >= 0
