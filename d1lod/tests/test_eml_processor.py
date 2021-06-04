import RDF

from d1lod.processors.eml.eml_processor import EMLProcessor

from .conftest import load_metadata, load_sysmeta
from d1lod.processors.util import model_has_statement


def test_processing_twice_works_right(client, model):
    simple = load_metadata("eml/eml-simple.xml")
    sysmeta = load_sysmeta("eml-simple-sysmeta.xml")

    processor = EMLProcessor(client, model, sysmeta, simple, [])

    processor.process()
    len_before = len(processor.model)
    processor.process()
    len_after = len(processor.model)

    assert len_before == len_after


def test_attributes_are_extracted(client, model):
    metadata = load_metadata("eml/eml-annotation-gym.xml")
    sysmeta = load_sysmeta("eml-annotation-gym-sysmeta.xml")

    processor = EMLProcessor(client, model, sysmeta, metadata, [])
    processor.process()

    statement = RDF.Statement(
        None,
        RDF.Node(RDF.Uri("http://schema.org/propertyID")),
        RDF.Node(RDF.Uri("http://purl.dataone.org/odo/ECSO_00001197")),
    )

    assert model_has_statement(processor.model, statement)
