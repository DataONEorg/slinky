import RDF

import d1lod.processors.util as util


def test_is_doi_works():
    # Negative cases
    assert not util.is_doi("foo")
    assert not util.is_doi("urn:uuid:1234-5678")

    # Positive cases
    assert util.is_doi("10.5063/F1891459")
    assert util.is_doi("doi:10.5063/F1891459")
    assert util.is_doi("https://doi.org/10.5063/F1891459")
    assert util.is_doi("https://dx.doi.org/10.5063/F1891459")
    assert util.is_doi("http://dx.doi.org/10.5063/F1891459")
    assert util.is_doi("http://dx.doi.org/10.5063/F1891459?query_params")


def test_get_doi_works():
    # Negative cases
    assert util.get_doi("foo") is None
    assert util.get_doi("urn:uuid:1234-5678") is None

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
    assert not util.is_orcid("foo")
    assert not util.is_orcid("urn:uuid:1234-5678")

    # Positive cases
    assert util.is_orcid("https://orcid.org/0000-0003-4703-1974")
    assert util.is_orcid("http://orcid.org/0000-0003-4703-1974")
    assert util.is_orcid("http://orcid.org/0000-0003-4703-197X")
    assert util.is_orcid("orcid.org/0000-0003-4703-1974")
    assert util.is_orcid("https://orcid.org/0000-0003-4703-1974")
    assert util.is_orcid("0000-0003-4703-1974")
    assert util.is_orcid("0000-0003-4703-197X")


def test_get_orcid_works():
    # Negative cases
    assert util.get_orcid("foo") is None
    assert util.get_orcid("urn:uuid:1234-5678") is None

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


def test_model_has_statement_finds_nothing_when_model_is_empty(model):
    assert not util.model_has_statement(
        model,
        RDF.Statement(None, None, None),
    )

    assert not util.model_has_statement(
        model,
        RDF.Statement(None, RDF.Node(RDF.Uri("http://example.com/predicate")), None),
    )

    assert not util.model_has_statement(
        model,
        RDF.Statement(
            RDF.Node(RDF.Uri("http://example.com/subject")),
            RDF.Node(RDF.Uri("http://example.com/predicate")),
            RDF.Node(RDF.Uri("http://example.com/object")),
        ),
    )


def test_model_has_statement_works_correctly(model):
    s1 = RDF.Statement(
        RDF.Node(RDF.Uri("http://example.com/subject")),
        RDF.Node(RDF.Uri("http://example.com/predicate")),
        RDF.Node(RDF.Uri("http://example.com/object")),
    )

    blanktest = RDF.Statement(
        RDF.Node(blank="myblank"),
        RDF.Node(RDF.Uri("http://example.com/blankpredicate")),
        RDF.Node("myblankliteral"),
    )

    literaltest = RDF.Statement(
        RDF.Node(RDF.Uri("http://example.com/literalsubject")),
        RDF.Node(RDF.Uri("http://example.com/literalpredicate")),
        RDF.Node("literalvalue"),
    )

    model.append(s1)
    model.append(blanktest)
    model.append(literaltest)

    assert util.model_has_statement(
        model,
        RDF.Statement(None, RDF.Node(RDF.Uri("http://example.com/predicate")), None),
    )

    assert not util.model_has_statement(
        model,
        RDF.Statement(None, RDF.Node(), None),
    )

    # Can find any statement with a given literal
    assert util.model_has_statement(
        model,
        RDF.Statement(None, None, RDF.Node("literalvalue")),
    )

    # Can find statements about a blank node
    assert util.model_has_statement(
        model,
        RDF.Statement(
            None,
            RDF.Node(RDF.Uri("http://example.com/blankpredicate")),
            RDF.Node("myblankliteral"),
        ),
    )
