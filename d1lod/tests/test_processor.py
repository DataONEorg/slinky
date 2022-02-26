import RDF

from d1lod.processors.processor import Processor

from .conftest import load_metadata, load_sysmeta
from d1lod.processors.util import model_has_statement


def test_processor_sets_checksum_and_algorithm(client, model):
    metadata = load_metadata("eml/eml-attribute-gym.xml")
    sysmeta = load_sysmeta("eml-attribute-gym-sysmeta.xml")

    processor = Processor(client, model, sysmeta, metadata, [])
    processor.process()

    assert model_has_statement(
        processor.model,
        RDF.Statement(
            None,
            RDF.Node(RDF.Uri("http://spdx.org/rdf/terms#algorithm")),
            None,
        ),
    )

    assert model_has_statement(
        processor.model,
        RDF.Statement(
            None,
            RDF.Node(RDF.Uri("http://spdx.org/rdf/terms#checksumValue")),
            None,
        ),
    )
