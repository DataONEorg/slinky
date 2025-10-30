from slinky.filtered_d1_client import FilteredCoordinatingNodeClient, BASE_FILTER


def test_combine_filters_works():
    client = FilteredCoordinatingNodeClient()
    assert client.combine_filters({}) == BASE_FILTER


def test_that_params_in_base_are_included():
    base = {"q": "id:foo"}
    extra = {}
    client = FilteredCoordinatingNodeClient(base)

    assert client.combine_filters(extra)["q"].find(BASE_FILTER["q"]) >= 0


def test_that_params_not_in_base_are_still_added():
    extra = {"facet": "true"}
    client = FilteredCoordinatingNodeClient()

    assert client.combine_filters(extra)["facet"] == "true"


def test_that_params_in_extra_are_anded():
    base = {"q": "formatType:METADATA"}
    extra = {"q": "id:foo"}
    client = FilteredCoordinatingNodeClient(base)

    final = client.combine_filters(extra)

    assert (
        final["q"]
        == "formatType:METADATA AND -obsoletedBy:* AND formatType:METADATA AND id:foo"
    )


def test_other_overrides_just_replace():
    base = {"rows": "1000"}
    extra = {"rows": "1001"}
    client = FilteredCoordinatingNodeClient(base)

    final = client.combine_filters(extra)

    assert final["rows"] == "1001"


def test_a_realistic_example():
    base = {
        "q": 'datasource:"urn:node:KNB" AND project:"State of Alaska\'s Salmon and People"',
        "rows": "100",
        "fl": "identifier",
        "wt": "json",
    }
    extra = {"q": "identifier:foo"}

    client = FilteredCoordinatingNodeClient(base)

    final = client.combine_filters(extra)

    assert final == {
        "q": 'formatType:METADATA AND -obsoletedBy:* AND datasource:"urn:node:KNB" AND project:"State of Alaska\'s Salmon and People" AND identifier:foo',
        "rows": "100",
        "fl": "identifier",
        "wt": "json",
    }


def test_that_date_modified_is_added_correctly():
    base = {"q": "formatType:METADATA"}
    extra = {"q": "dateModified:[A TO B]"}
    client = FilteredCoordinatingNodeClient(base)

    final = client.combine_filters(extra)

    assert (
        final["q"]
        == "formatType:METADATA AND -obsoletedBy:* AND formatType:METADATA AND dateModified:[A TO B]"
    )
