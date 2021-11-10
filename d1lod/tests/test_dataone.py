"""test_dataone.py

Test the DataOne utility library.
"""

from d1lod.legacy import dataone


def test_parsing_resource_map():
    pid = "resourceMap_df35d.3.2"

    aggd_pids = dataone.getAggregatedIdentifiers(pid)

    assert len(aggd_pids) == 7


def test_extracting_identifiers_from_urls():
    # Returns None when it should
    assert dataone.extractIdentifierFromFullURL("asdf") is None
    assert dataone.extractIdentifierFromFullURL(1) is None
    assert dataone.extractIdentifierFromFullURL("1") is None
    assert dataone.extractIdentifierFromFullURL("http://google.com") is None

    # Extracts the right thing
    assert (
        dataone.extractIdentifierFromFullURL(
            "https://cn.dataone.org/cn/v1/meta/some_pid"
        )
        == "some_pid"
    )
    assert (
        dataone.extractIdentifierFromFullURL(
            "https://cn.dataone.org/cn/v1/meta/kgordon.23.30"
        )
        == "kgordon.23.30"
    )
    assert (
        dataone.extractIdentifierFromFullURL(
            "https://cn.dataone.org/cn/v1/resolve/kgordon.23.30"
        )
        == "kgordon.23.30"
    )
    assert (
        dataone.extractIdentifierFromFullURL(
            "https://cn.dataone.org/cn/v1/object/kgordon.23.30"
        )
        == "kgordon.23.30"
    )
    assert (
        dataone.extractIdentifierFromFullURL(
            "https://cn.dataone.org/cn/v2/object/kgordon.23.30"
        )
        == "kgordon.23.30"
    )
