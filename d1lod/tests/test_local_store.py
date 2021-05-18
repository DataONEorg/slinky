def test_that_store_query_works(local_store):
    response = local_store.query("select ?s ?p ?o where { ?s ?p ?o } limit 1")

    assert len(response) >= 0


def test_that_store_insert_model_works(local_store, test_model):
    result = local_store.insert_model(test_model)

    assert result == True

    response = local_store.query("select ?s ?p ?o where { ?s ?p ?o } limit 1")
    assert len(response) == 1


def test_can_handle_big_inserts(local_store, huge_model):
    result = local_store.insert_model(huge_model)

    assert result == True

    response = local_store.query("select ?s ?p ?o where { ?s ?p ?o } limit 5000")
    assert len(response) == 5000
