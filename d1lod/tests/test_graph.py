import pytest
import RDF

from d1lod.graph import Graph


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

    payload_data = "<%s> %s %s" % (RDF.Uri('http://example.org/#Foo'), "?p", "?o")

    graph.delete_data(payload=payload_data)
    assert graph.size() == 0


def clear_graphs(graph):
    graphs = graph.graphs()

    for graph_name in graphs:
        if graph_name == "SYSTEM":
            continue

        graph.delete_graph(graph_name, silent=True)


def test_graph_can_be_created(graph):
    assert isinstance(graph, Graph)


def test_graphs_can_be_created(graph):
    temp = graph.name

    if graph.exists():
        print("Graph already exists. Deleting it..")
        graph.delete_graph ()

    graph.create_graph()

    assert graph.exists() == "true"

    graph.name = temp


def test_graphs_can_be_deleted(graph):
    temp = graph.name

    graph.name = "test_to_delete_graph"

    assert graph.exists()

    graph.create_graph()

    assert graph.exists()

    graph.delete_graph()

    assert graph.exists()

    graph.name = temp


def test_graph_can_list_its_graphs(graph):
    # clear_graphs(graph)


    graph.name = "canadd"
    graph.create_graph()

    graph.insert(s=RDF.Uri('http://example.org/#Foo'),
                 p=RDF.Uri('http://example.org/#isA'),
                 o=RDF.Uri('http://name.org/Foo'))


    assert 'canadd' in graph.graphs()
