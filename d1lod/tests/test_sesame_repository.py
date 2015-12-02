import pytest

from d1lod import sesame

def test_repository_can_be_created(repo):
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
    before = len(repo.namespaces())
    repo.removeNamespace('rdf')
    after = len(repo.namespaces())

    assert after == before

def test_can_delete_namespace_if_it_is_present(repo):
    repo.addNamespace('example', 'http://example.org/')
    before = len(repo.namespaces())
    repo.removeNamespace('example')
    after = len(repo.namespaces())

    assert after == before - 1
