import pytest

import d1lod.processors.util as util


def test_is_doi_works():
    # Negative cases
    assert util.is_doi("foo") == False
    assert util.is_doi("urn:uuid:1234-5678") == False

    # Positive cases
    assert util.is_doi("10.5063/F1891459") == True
    assert util.is_doi("doi:10.5063/F1891459") == True
    assert util.is_doi("https://doi.org/10.5063/F1891459") == True
    assert util.is_doi("https://dx.doi.org/10.5063/F1891459") == True
    assert util.is_doi("http://dx.doi.org/10.5063/F1891459") == True
    assert util.is_doi("http://dx.doi.org/10.5063/F1891459?query_params") == True


def test_get_doi_works():
    # Negative cases
    assert util.get_doi("foo") == None
    assert util.get_doi("urn:uuid:1234-5678") == None

    # Positive cases
    assert util.get_doi("10.5063/F1891459") == "10.5063/F1891459"
    assert util.get_doi("doi:10.5063/F1891459") == "10.5063/F1891459"
    assert util.get_doi("https://doi.org/10.5063/F1891459") == "10.5063/F1891459"
    assert util.get_doi("https://dx.doi.org/10.5063/F1891459") == "10.5063/F1891459"
    assert util.get_doi("http://dx.doi.org/10.5063/F1891459") == "10.5063/F1891459"
    assert (
        util.get_doi("http://dx.doi.org/10.5063/F1891459?query_params")
        == "10.5063/F1891459"
    )


def test_is_orcid_works():
    # Negative cases
    assert util.is_orcid("foo") == False
    assert util.is_orcid("urn:uuid:1234-5678") == False

    # Positive cases
    assert util.is_orcid("https://orcid.org/0000-0003-4703-1974") == True
    assert util.is_orcid("http://orcid.org/0000-0003-4703-1974") == True
    assert util.is_orcid("http://orcid.org/0000-0003-4703-197X") == True
    assert util.is_orcid("orcid.org/0000-0003-4703-1974") == True
    assert util.is_orcid("https://orcid.org/0000-0003-4703-1974") == True
    assert util.is_orcid("0000-0003-4703-1974") == True
    assert util.is_orcid("0000-0003-4703-197X") == True


def test_get_orcid_works():
    # Negative cases
    assert util.get_orcid("foo") == None
    assert util.get_orcid("urn:uuid:1234-5678") == None

    # Positive cases
    assert (
        util.get_orcid("https://orcid.org/0000-0003-4703-1974") == "0000-0003-4703-1974"
    )
    assert (
        util.get_orcid("http://orcid.org/0000-0003-4703-1974") == "0000-0003-4703-1974"
    )
    assert (
        util.get_orcid("http://orcid.org/0000-0003-4703-197X") == "0000-0003-4703-197X"
    )
    assert util.get_orcid("orcid.org/0000-0003-4703-1974") == "0000-0003-4703-1974"
    assert (
        util.get_orcid("https://orcid.org/0000-0003-4703-1974") == "0000-0003-4703-1974"
    )
    assert util.get_orcid("0000-0003-4703-1974") == "0000-0003-4703-1974"
    assert util.get_orcid("0000-0003-4703-197X") == "0000-0003-4703-197X"
