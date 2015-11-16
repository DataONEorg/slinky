import pytest

from d1lod import sesame

@pytest.fixture(scope="module")
def store():
    return sesame.Store('localhost', 8080)

@pytest.fixture(scope="module")
def repo(store):
    r = sesame.Repository(store, 'test')
    r.clear()

    return r

@pytest.fixture(scope="module")
def interface(repo):
    return sesame.Interface(repo)
