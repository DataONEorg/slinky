import pytest

from d1lod import sesame

def test_repository_can_be_created(repo):
    assert isinstance(repo, sesame.Repository)

def test_triples_can_be_added(repo):
    assert repo.size() == 0
    repo.insert({'s':'owl:Thing', 'p':'rdf:type', 'o':'owl:OtherThing'})
    assert repo.size() == 1
