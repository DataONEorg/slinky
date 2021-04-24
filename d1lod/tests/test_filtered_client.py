import pytest
from d1lod.filtered_client import FilteredCoordinatingNodeClient

def test_combine_filters_works():
    client = FilteredCoordinatingNodeClient()
    assert client.combine_filters({}) == {}


def test_that_params_in_base_are_included():
    base = {'q':'id:foo'}
    extra = {}
    client = FilteredCoordinatingNodeClient(base)

    assert client.combine_filters(extra) == base


def test_that_params_not_in_base_are_still_added():
    base = {}
    extra = {'q':'id:foo'}
    client = FilteredCoordinatingNodeClient(base)

    assert client.combine_filters(extra) == extra


def test_that_params_in_extra_are_anded():
    base = {'q':'formatType:METADATA'}
    extra = {'q':'id:foo'}
    client = FilteredCoordinatingNodeClient(base)

    final = client.combine_filters(extra)

    assert final['q'] == 'formatType:METADATA AND id:foo'


def test_other_overrides_just_replace():
    base = {'rows':'1000'}
    extra = {'rows':'1001'}
    client = FilteredCoordinatingNodeClient(base)

    final = client.combine_filters(extra)

    assert final['rows'] == '1001'


def test_a_realistic_example():
    base = {
        'q':'datasource:"urn:node:KNB" AND project:"State of Alaska\'s Salmon and People" AND formatType:METADATA AND -obsoletedBy:*',
        'rows': '100',
        'fl': 'identifier',
        'wt': 'json'
    }
    extra = { 'q': 'identifier:foo'}

    client = FilteredCoordinatingNodeClient(base)

    final = client.combine_filters(extra)

    assert final == {
        'q':'datasource:"urn:node:KNB" AND project:"State of Alaska\'s Salmon and People" AND formatType:METADATA AND -obsoletedBy:* AND identifier:foo',
        'rows': '100',
        'fl': 'identifier',
        'wt': 'json'
    }
