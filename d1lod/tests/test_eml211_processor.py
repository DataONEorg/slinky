import textwrap
import RDF

from d1lod.processors.eml.eml210_processor import EML210Processor
from d1lod.processors.util import model_has_statement

from .conftest import load_metadata, load_sysmeta


# Tests that the processor extracts the non-complex (ie not people) top level eml dataset attributes:
# alternateIdentifier, title, abstract, pubDate, keywordSet
def test_processor_extracts_top_metadata(client, model):
    metadata = load_metadata("eml/eml-211.xml")
    sysmeta = load_sysmeta("eml-211-sysmeta.xml")

    processor = EML210Processor(client, model, sysmeta, metadata, [])
    processor.process()
    node_id = "https://dataone.org/datasets/eml-211"

    # Create the alternateIdentifier node
    statement = RDF.Statement(
        RDF.Node(RDF.Uri(node_id)),
        RDF.Node(RDF.Uri("https://schema.org/identifier")),
        RDF.Node("311"),
    )
    assert model_has_statement(processor.model, statement)
    # Create the title node
    statement = RDF.Statement(
        RDF.Node(RDF.Uri(node_id)),
        RDF.Node(RDF.Uri("https://schema.org/name")),
        RDF.Node("Gut Fluorescence measurements of mesozooplankton grazing on autotrophic prey. "
                 "Samples collected in the CCE-LTER region on Process Cruises from 2006 to the present. "
                 "Summaries for each Lagrangian Cycle."),
    )
    assert model_has_statement(processor.model, statement)
    # Create the abstract node
    statement = RDF.Statement(
        RDF.Node(RDF.Uri(node_id)),
        RDF.Node(RDF.Uri("https://schema.org/description")),
        RDF.Node("Mesozooplankton are collected with plankton nets (typically a 71-cm diameter, 202-um mesh Bongo net)"
                 " and samples flash frozen at sea in liquid N2 for subsequent shore-based measurements of ingested "
                 "phytoplankton chlorophyll-a. Measurements of mesozooplankton gut fluorescence are done by "
                 "fluorometric analysis on a Turner Designs fluorometer of gut pigments extracted in 90% acetone. "
                 "Analyses are done on mesozooplankton size-fractionated into 5 different categories on Nitex mesh "
                 "(> 0.2 mm, 0.5 mm, 1.0 mm, 2.0 mm, 5.0 mm). The pigment content (as Chl-a and phaeopigments) is "
                 "then expressed as mass of pigment ingested per m3 of water filtered, or divided by the dry weight "
                 "biomass of the mesozooplankton in the same sample in order to obtain mass-specific ingestion per "
                 "m3 of water. Application of published values of the temperature-dependent gut passage time are used "
                 "to estimate the mesozooplankton grazing rate, as pigments ingested per m3 per unit time, or the "
                 "corresponding mass-specific rate of ingestion. Samples for gut fluorescence assays have been "
                 "collected on CCE-LTER Process Cruises since 2006 and these collections are ongoing."),
    )
    assert model_has_statement(processor.model, statement)
    # Create the pubDate node
    statement = RDF.Statement(
        RDF.Node(RDF.Uri(node_id)),
        RDF.Node(RDF.Uri("https://schema.org/datePublished")),
        RDF.Node("2021-10-29"),
    )
    assert model_has_statement(processor.model, statement)
    for keyword in ["biogeochemistry", "carbon flux", "chlorophyll a", "grazing", "herbivory",
                    "Mesozooplankton"]:
        # Create the keywordSet node
        statement = RDF.Statement(
            RDF.Node(RDF.Uri(node_id)),
            RDF.Node(RDF.Uri("https://schema.org/keyword")),
            RDF.Node(keyword),
        )
        assert model_has_statement(processor.model, statement)
