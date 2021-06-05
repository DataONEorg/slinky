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
