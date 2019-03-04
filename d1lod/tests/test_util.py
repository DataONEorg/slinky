"""test_util.py"""


from d1lod.d1lod import util


def test_can_match_doi_strings():
    """Tests the matching algorithm which takes unstructured strings and guesses
    their identifier structure using string-matching.
    """

    assert util.getIdentifierScheme("http://doi.org/10.XX") == "doi"
    assert util.getIdentifierScheme("https://doi.org/10.XX") == "doi"
    assert util.getIdentifierScheme("doi:10.XX") == "doi"
    assert util.getIdentifierScheme("ark://1234") == "ark"
    assert util.getIdentifierScheme("somethingsomething") != "doi"
    assert util.getIdentifierScheme("somethingsomething") == "local-resource-identifier-scheme"


def test_can_determine_resolve_urls():
    # DOIs
    assert util.getIdentifierResolveURL('http://doi.org/10.asdf') == 'http://doi.org/10.asdf'
    assert util.getIdentifierResolveURL('doi:/10.asdf') == 'http://doi.org/10.asdf'
    assert util.getIdentifierResolveURL('http://dx.doi.org/10.asdf') == 'http://doi.org/10.asdf'

    # URIs
    assert util.getIdentifierResolveURL('http://example.org') == 'http://example.org'

    # DataOne PIDs
    assert util.getIdentifierResolveURL('asdf') == 'https://cn.dataone.org/cn/v1/resolve/asdf'

    # Bad values
    assert util.getIdentifierResolveURL('') is None
    assert util.getIdentifierResolveURL(1) is None
    assert util.getIdentifierResolveURL(None) is None
