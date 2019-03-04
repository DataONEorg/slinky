import pytest
import RDF

from d1lod.d1lod.graph import Graph


def test_graph_object_can_be_created(graph):
    assert isinstance(graph, Graph)


def test_graph_can_be_cleared(graph):
    graph.clear()

    assert graph.size() == 0


def test_graph_can_tell_us_its_size(graph):
    graph.clear()
    assert graph.size() == 0


def test_graph_can_tell_us_its_namespaces(graph):
    graph.clear()

    graph.ns = {
        "geolink": "http://schema.geolink.org/1.0/base/main#"
    }
    ns = graph.namespacePrefixString()

    assert len(ns) > 0


def test_can_insert_a_triple(graph):
    graph.clear()
    assert graph.size() == 0

    graph.insert(s=RDF.Uri('http://example.org/#Foo'),
                p=RDF.Uri('http://example.org/#isA'),
                o=RDF.Uri('http://name.org/Foo'))

    assert graph.size() == 1


def test_can_delete_triples(graph):
    graph.clear()
    assert graph.size() == 0

    graph.insert(s=RDF.Uri('http://example.org/#Foo'),
                p=RDF.Uri('http://example.org/#isA'),
                o=RDF.Uri('http://name.org/Foo'))

    assert graph.size() == 1

    payload_data = u"%s %s %s" % (RDF.Uri('http://example.org/#Foo'), "?p", "?o")

    graph.delete_data(payload=payload_data)
    assert graph.size() == 0


def clear_graphs(store):
    graphs = store.graphs()

    for graph in graphs:
        if graph == "SYSTEM":
            continue

        store.delete_graph(graph)


def test_store_can_be_created(store):
    assert isinstance(store, Graph)


def test_graphs_can_be_created(store):
    graph_to_create = 'test'

    if store.exists(graph_to_create):
        print "Graph already exists. Deleting it.."
        store.delete_graph (graph_to_create)

    store.create_graph(graph_to_create)

    assert store.exists(graph_to_create) == "true"


def test_graphs_can_be_deleted(store):
    clear_graphs(store)
    graph_to_delete = 'test'

    assert store.exists(graph_to_delete) == "false"

    store.create_graph(graph_to_delete)

    assert store.exists(graph_to_delete) == "true"

    store.delete_graph(graph_to_delete)

    assert store.exists(graph_to_delete) == "false"


def test_store_can_list_its_graphs(store):
    clear_graphs(store)

    store.create_graph('canadd')
    assert 'canadd' in store.graphs()
