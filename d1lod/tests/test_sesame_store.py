import pytest

from d1lod import sesame

def clear_repositories(store):
    repos = store.repositories()

    for repo in repos:
        if repo == "SYSTEM":
            continue

        store.deleteRepository(repo)

def test_store_can_be_created(store):
    assert isinstance(store, sesame.Store)

def test_repositories_can_be_created(store):
    clear_repositories(store)
    repo_to_create = 'test'

    assert repo_to_create not in store.repositories()

    store.createRepository(repo_to_create)

    assert repo_to_create in store.repositories()

def test_repositories_can_be_delete(store):
    clear_repositories(store)
    repo_to_delete = 'test'

    assert repo_to_delete not in store.repositories()

    store.createRepository(repo_to_delete)

    assert repo_to_delete in store.repositories()

    store.deleteRepository(repo_to_delete)

    assert repo_to_delete not in store.repositories()

def test_store_has_a_protocol(store):
    assert store.protocol() == '6'

def test_store_can_list_its_repositories(store):
    clear_repositories(store)

    assert store.repositories() == [ 'SYSTEM' ]

    store.createRepository('canadd')
    assert 'canadd' in store.repositories()
