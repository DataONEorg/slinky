import pytest

from d1lod import sesame

@pytest.fixture(scope="module")
def store():
    return sesame.Store('localhost', 8080)

@pytest.fixture(scope="module")
def repo(store):
    return sesame.Repository(store, 'test')

@pytest.fixture(scope="module")
def interface(repo):
    return sesame.Interface(repo)
