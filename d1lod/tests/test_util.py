"""test_util.py"""


from d1lod import util


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
