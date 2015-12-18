import pytest
import RDF

from d1lod import sesame


def test_repository_object_can_be_created(repo):
    assert isinstance(repo, sesame.Repository)


def test_repository_can_be_cleared(repo):
    repo.clear()

    assert repo.size() == 0


def test_repository_can_tell_us_its_size(repo):
    repo.clear()
    assert repo.size() == 0


def test_repository_can_be_exported(repo):
    repo.clear()

    txt = repo.export()
    assert txt.startswith("@prefix")


def test_repository_can_list_its_statements(repo):
    repo.clear()

    txt = repo.export()
    assert txt.startswith("@prefix")


def test_repository_can_tell_us_its_namespaces(repo):
    repo.clear()

    ns = repo.namespaces()

    assert len(ns) > 0


def test_can_get_namespace(repo):
    assert repo.getNamespace('rdf') == 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'


def test_can_delete_namespace_if_none_are_present(repo):
    repo.removeNamespace('xxx')


def test_can_delete_namespace_if_it_is_present(repo):
    repo.addNamespace('example', 'http://example.org/')
    before = len(repo.namespaces())
    repo.removeNamespace('example')
    after = len(repo.namespaces())

    assert after == before - 1


def test_can_insert_a_triple(repo):
    repo.clear()
    assert repo.size() == 0

    repo.insert(s=RDF.Uri('http://example.org/#Foo'),
                p=RDF.Uri('http://example.org/#isA'),
                o=RDF.Node('Foo'))

    assert repo.size() == 1


def test_can_insert_a_triple_with_context(repo):
    repo.clear()
    assert repo.size() == 0
    assert len(repo.contexts()) == 0

    repo.insert(s=RDF.Uri('http://example.org/#Foo'),
                p=RDF.Uri('http://example.org/#isA'),
                o=RDF.Node('Foo'),
                context='foo')

    assert repo.size() == 1
    assert len(repo.contexts()) == 1


def test_can_delete_triples_about_a_subject_without_a_context(repo):
    repo.clear()
    assert repo.size() == 0

    repo.insert(s=RDF.Uri('http://example.org/#Foo'),
                p=RDF.Uri('http://example.org/#isA'),
                o=RDF.Node('Foo'))

    assert repo.size() == 1

    repo.delete_triples_about(RDF.Uri('http://example.org/#Foo'))
    assert repo.size() == 0


def test_can_delete_statements_about_a_subject_with_a_context(repo):
    repo.clear()
    assert repo.size() == 0
    assert len(repo.contexts()) == 0

    repo.insert(s=RDF.Uri('http://example.org/#Foo'),
                p=RDF.Uri('http://example.org/#isA'),
                o=RDF.Node('Foo'),
                context='foo')

    assert repo.contexts() == [{'contextID':'<http://localhost:8080/openrdf-sesame/repositories/test/rdf-graphs/foo>'}]

    repo.delete_triples_about(RDF.Uri('http://example.org/#Foo'), context='foo')
    assert repo.size() == 0
    assert len(repo.contexts()) == 0


def test_can_import_rdf_from_a_file(repo):
    repo.clear()
    assert repo.size() == 0

    repo.import_from_file('./tests/data/simple_graph.ttl', fmt='turtle')

    assert repo.size() == 1


def test_can_import_rdf_from_a_file(repo):
    repo.clear()
    assert repo.size() == 0

    repo.import_from_file('./tests/data/simple_graph.ttl', context='testcontext', fmt='turtle')

    assert repo.size() == 1
