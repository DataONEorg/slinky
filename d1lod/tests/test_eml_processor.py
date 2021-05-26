from d1lod.processors.eml.eml220_processor import EML220Processor

from .conftest import load_metadata, load_sysmeta, print_model


def test_processing_twice_works_right(client, model):
    simple = load_metadata("eml/eml-simple.xml")
    sysmeta = load_sysmeta("eml-simple-sysmeta.xml")

    processor = EML220Processor(client, model, sysmeta, simple, [])

    processor.process()
    len_before = len(processor.model)
    processor.process()
    len_after = len(processor.model)

    assert len_before == len_after
