import pytest

from d1lod.sesame import store as sesamestore
from d1lod.sesame import repository
from d1lod.sesame import interface as sesint


@pytest.fixture(scope="module")
def store():
    return sesamestore.SesameStore('localhost', 8080)

@pytest.fixture(scope="module")
def repo(store):
    r = repository.SesameRepository(store, 'test')
    r.clear()

    return r

@pytest.fixture(scope="module")
def interface(repo):
    return sesint.SesameInterface(repo)
