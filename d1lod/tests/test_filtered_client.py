import pytest
from d1lod.filtered_d1_client import FilteredCoordinatingNodeClient, DEFAULT_FILTER


def test_combine_filters_works():
    client = FilteredCoordinatingNodeClient()
    assert client.combine_filters({}) == DEFAULT_FILTER


def test_that_params_in_base_are_included():
    base = {"q": "id:foo"}
    extra = {}
    client = FilteredCoordinatingNodeClient(base)

    assert client.combine_filters(extra) == {**DEFAULT_FILTER, **base}


def test_that_params_not_in_base_are_still_added():
    extra = {"facet": True}
    client = FilteredCoordinatingNodeClient()

    assert client.combine_filters(extra) == {**DEFAULT_FILTER, **extra}


def test_that_params_in_extra_are_anded():
    base = {"q": "formatType:METADATA"}
    extra = {"q": "id:foo"}
    client = FilteredCoordinatingNodeClient(base)

    final = client.combine_filters(extra)

    assert final["q"] == "formatType:METADATA AND id:foo"


def test_other_overrides_just_replace():
    base = {"rows": "1000"}
    extra = {"rows": "1001"}
    client = FilteredCoordinatingNodeClient(base)

    final = client.combine_filters(extra)

    assert final["rows"] == "1001"


def test_a_realistic_example():
    base = {
        "q": 'datasource:"urn:node:KNB" AND project:"State of Alaska\'s Salmon and People" AND formatType:METADATA AND -obsoletedBy:*',
        "rows": "100",
        "fl": "identifier",
        "wt": "json",
    }
    extra = {"q": "identifier:foo"}

    client = FilteredCoordinatingNodeClient(base)

    final = client.combine_filters(extra)

    assert final == {
        "q": 'datasource:"urn:node:KNB" AND project:"State of Alaska\'s Salmon and People" AND formatType:METADATA AND -obsoletedBy:* AND identifier:foo',
        "rows": "100",
        "fl": "identifier",
        "wt": "json",
    }


def test_that_date_modifieid_is_added_correctly():
    base = {"q": "formatType:METADATA"}
    extra = {"q": "dateModified:[A TO B]"}
    client = FilteredCoordinatingNodeClient(base)

    final = client.combine_filters(extra)

    assert final["q"] == "formatType:METADATA AND dateModified:[A TO B]"
