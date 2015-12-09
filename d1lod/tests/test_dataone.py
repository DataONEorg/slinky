"""test_dataone.py

Test the DataOne utility library.
"""

from d1lod.dataone import extractIdentifierFromFullURL as extract

def test_extracting_identifiers_from_urls():
    # Returns None when it should
    assert extract('asdf') is None
    assert extract(1) is None
    assert extract('1') is None
    assert extract('http://google.com') is None

    # Extracts the right thing
    assert extract('https://cn.dataone.org/cn/v1/meta/some_pid') == 'some_pid'
    assert extract('https://cn.dataone.org/cn/v1/meta/kgordon.23.30') == 'kgordon.23.30'
    assert extract('https://cn.dataone.org/cn/v1/resolve/kgordon.23.30') == 'kgordon.23.30'
    assert extract('https://cn.dataone.org/cn/v1/object/kgordon.23.30') == 'kgordon.23.30'
    assert extract('https://cn.dataone.org/cn/v2/object/kgordon.23.30') == 'kgordon.23.30'
