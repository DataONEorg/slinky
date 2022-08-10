import RDF

from slinky.processors.eml.eml210_processor import EML210Processor
from slinky.processors.util import model_has_statement
from slinky.namespaces import NS_SCHEMA

from .conftest import load_metadata, load_sysmeta


# Tests that the processor extracts the non-complex (ie not people) top level eml dataset attributes:
# alternateIdentifier, title, abstract, pubDate, keywordSet
def test_processor_extracts_top_metadata(client, model):
    metadata = load_metadata("eml/eml-201.xml")
    sysmeta = load_sysmeta("eml-201-sysmeta.xml")

    processor = EML210Processor(client, model, sysmeta, metadata, [])
    processor.process()
    node_id = "https://dataone.org/datasets/doi%3A10.6085%2FAA%2FICMDXX_XXXITV2XMSR01_20170101.50.1"

    # Create the alternateIdentifier node
    statement = RDF.Statement(
        RDF.Node(RDF.Uri(node_id)),
        RDF.Node(RDF.Uri(NS_SCHEMA.identifier)),
        RDF.Node("doi:10.6085/AA/ICMDXX_XXXITV2XMSR01_20170101.50.1"),
    )
    assert model_has_statement(processor.model, statement)
    # Create the title node
    statement = RDF.Statement(
        RDF.Node(RDF.Uri(node_id)),
        RDF.Node(RDF.Uri(NS_SCHEMA.name)),
        RDF.Node(
            "MARINe/PISCO: Intertidal: site temperature data: Cape Mendocino (ICMDXX)"
        ),
    )
    assert model_has_statement(processor.model, statement)
    # Create the abstract node
    statement = RDF.Statement(
        RDF.Node(RDF.Uri(node_id)),
        RDF.Node(RDF.Uri(NS_SCHEMA.description)),
        RDF.Node(
            "This metadata record describes a mix of intertidal seawater and air "
            "temperature data collected at Cape Mendocino by MARINe/PISCO. Measurements were collected "
            "using Temperature Loggers from Onset Computer Corp"
        ),
    )
    assert model_has_statement(processor.model, statement)
    # Create the pubDatenode
    statement = RDF.Statement(
        RDF.Node(RDF.Uri(node_id)),
        RDF.Node(RDF.Uri(NS_SCHEMA.datePublished)),
        RDF.Node("2019-09-26"),
    )
    assert model_has_statement(processor.model, statement)
    for keyword in [
        "EARTH SCIENCE : Oceans : Ocean Temperature : Water Temperature",
        "Temperature",
        "Integrated Ocean Observing System",
        "IOOS",
        "Oceanographic Sensor Data",
        "Intertidal Temperature Data",
        "continental shelf",
        "seawater",
        "temperature",
    ]:
        # Create the keywordSet node
        statement = RDF.Statement(
            RDF.Node(RDF.Uri(node_id)),
            RDF.Node(RDF.Uri(NS_SCHEMA.keyword)),
            RDF.Node(keyword),
        )
        assert model_has_statement(processor.model, statement)
