import RDF

from d1lod.processors.eml.eml_processor import EMLProcessor

from .conftest import load_metadata, load_sysmeta
from d1lod.processors.util import model_has_statement


def test_attributes_are_extracted_correctly(client, model):
    metadata = load_metadata("eml/eml-attribute-gym.xml")
    sysmeta = load_sysmeta("eml-attribute-gym-sysmeta.xml")

    processor = EMLProcessor(client, model, sysmeta, metadata, [])
    processor.process()

    assert model_has_statement(
        processor.model,
        RDF.Statement(
            None,
            RDF.Node(RDF.Uri("https://schema.org/variableMeasured")),
            None,
        ),
    )

    assert model_has_statement(
        processor.model,
        RDF.Statement(
            None,
            RDF.Node(RDF.Uri("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")),
            RDF.Node(RDF.Uri("https://schema.org/PropertyValue")),
        ),
    )

    assert model_has_statement(
        processor.model,
        RDF.Statement(
            None,
            RDF.Node(RDF.Uri("https://schema.org/name")),
            RDF.Node("ExampleAttribute"),
        ),
    )

    assert model_has_statement(
        processor.model,
        RDF.Statement(
            None,
            RDF.Node(RDF.Uri("https://schema.org/alternateName")),
            RDF.Node("Example Attribute"),
        ),
    )

    assert model_has_statement(
        processor.model,
        RDF.Statement(
            None,
            RDF.Node(RDF.Uri("https://schema.org/description")),
            RDF.Node("ExampleAttributeDefinition"),
        ),
    )

    assert model_has_statement(
        processor.model,
        RDF.Statement(
            None,
            RDF.Node(RDF.Uri("https://schema.org/propertyID")),
            RDF.Node(RDF.Uri("http://purl.dataone.org/odo/ECSO_00001197")),
        ),
    )


def test_attribute_with_annotations_are_extracted_correctly(client, model):
    metadata = load_metadata("eml/eml-annotation-gym.xml")
    sysmeta = load_sysmeta("eml-annotation-gym-sysmeta.xml")

    processor = EMLProcessor(client, model, sysmeta, metadata, [])
    processor.process()

    statement = RDF.Statement(
        None,
        RDF.Node(RDF.Uri("https://schema.org/propertyID")),
        RDF.Node(RDF.Uri("http://purl.dataone.org/odo/ECSO_00001197")),
    )

    assert model_has_statement(processor.model, statement)


# Test that the processor can handle 2.0.0 documents

# Tests that the processor extracts the non-complex (ie not people) top level eml dataset attributes:
# alternateIdentifier, title, abstract, pubDate, keywordSet


def test_processor_extracts_top_metadata(client, model):
    metadata = load_metadata("eml/eml-200.xml")
    sysmeta = load_sysmeta("eml-200-sysmeta.xml")

    processor = EMLProcessor(client, model, sysmeta, metadata, [])
    processor.process()
    node_id = "https://dataone.org/datasets/doi%3A10.5063%2FAA%2Fconnolly.116.1"

    # Create the alternateIdentifier node
    statement = RDF.Statement(
        RDF.Node(RDF.Uri(node_id)),
        RDF.Node(RDF.Uri("https://schema.org/identifier")),
        RDF.Node("doi:10.5063/AA/connolly.116.1"),
    )

    assert model_has_statement(processor.model, statement)
    # Create the title node
    statement = RDF.Statement(
        RDF.Node(RDF.Uri(node_id)),
        RDF.Node(RDF.Uri("https://schema.org/name")),
        RDF.Node(
            "Parallel effects of land-use history on species diversity and genetic diversity of forest herbs."
        ),
    )
    assert model_has_statement(processor.model, statement)
    # Create the abstract node
    statement = RDF.Statement(
        RDF.Node(RDF.Uri(node_id)),
        RDF.Node(RDF.Uri("https://schema.org/description")),
        RDF.Node(
            "The two most fundamental levels of biodiversity, species diversity and genetic diversity, are "
            "seldom studied simultaneously despite a strikingly similar set of processes that underlie "
            "patterns at the two levels. Agricultural land use drastically reduces populations of forest "
            "herbs in the north-temperate zone, so that bottlenecks or founder events in forests on abandoned "
            "agricultural land (i.e., secondary forests) may have a long-term impact on both species "
            "diversity and genetic diversity. Using forest-herb community surveys and molecular-genetic "
            "analysis of populations of Trillium grandiflorum, a representative species of forest herb, "
            "I investigated the influence of land-use history, landscape context, and environmental "
            "conditions on diversity and divergence at the population and community levels. Secondary "
            "forests (70100 years old) had reduced diversity of both genes and species relative to primary "
            "forests (i.e., stands never cleared for agriculture). The community in secondary forests had "
            "an overrepresentation of the most common species in the landscape, though divergence in species' "
            "relative abundances within stands suggested an influence of community drift via local bottlenecks. "
            "Secondary-forest populations of T. grandiflorum were more genetically divergent than those in "
            "primary forests, again indicating drift in small populations. Land-use history and the size of "
            "populations and communities drove correlations between species diversity and genetic diversity "
            "(and community divergence \u00D7 genetic divergence), though the strength of correlations was "
            "relatively weak. These results extend the generality of positive speciesgenetic diversity "
            "correlations previously observed for islands, and they demonstrate a long-term legacy of land-use "
            "history at multiple levels of biodiversity."
        ),
    )
    assert model_has_statement(processor.model, statement)
    # Create the pubDatenode
    statement = RDF.Statement(
        RDF.Node(RDF.Uri(node_id)),
        RDF.Node(RDF.Uri("https://schema.org/datePublished")),
        RDF.Node("2020-01-01"),
    )
    assert model_has_statement(processor.model, statement)
    for keyword in [
        "biodiversity; forest herbs; genetic diversity; land-use history; species diversity; "
        "Tompkins County, New York (USA); forest stands; Trillium grandiflorum"
    ]:
        # Create the keywordSet node
        statement = RDF.Statement(
            RDF.Node(RDF.Uri(node_id)),
            RDF.Node(RDF.Uri("https://schema.org/keyword")),
            RDF.Node(keyword),
        )
        assert model_has_statement(processor.model, statement)


def test_extracts_standard_units(client, model):
    metadata = load_metadata("eml/eml-200.xml")
    sysmeta = load_sysmeta("eml-200-sysmeta.xml")

    processor = EMLProcessor(client, model, sysmeta, metadata, [])
    processor.process()

    statement = RDF.Statement(
        None,
        RDF.Node(RDF.Uri("https://schema.org/unitText")),
        RDF.Node("degree"),
    )

    assert statement in processor.model


def test_extracts_custom_units(client, model):
    metadata = load_metadata("eml/eml-data-paper.xml")
    sysmeta = load_sysmeta("eml-data-paper-sysmeta.xml")

    processor = EMLProcessor(client, model, sysmeta, metadata, [])
    processor.process()

    statement = RDF.Statement(
        None,
        RDF.Node(RDF.Uri("https://schema.org/unitText")),
        RDF.Node("arc_degree"),
    )

    assert model_has_statement(processor.model, statement)
