import pytest

from d1lod.sesame import repository

def test_repository_can_be_created(repo):
    assert isinstance(repo, repository.SesameRepository)

def test_triples_can_be_added(repo):
    assert repo.size() == 0
    repo.insert({'s':'owl:Thing', 'p':'rdf:type', 'o':'owl:OtherThing'})
    assert repo.size() == 1
