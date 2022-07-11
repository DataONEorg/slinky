import RDF

from d1lod.processors.eml.eml210_processor import EML210Processor
from d1lod.processors.util import model_has_statement

from .conftest import load_metadata, load_sysmeta


# Tests that the processor extracts the non-complex (ie not people) top level eml dataset attributes:
# alternateIdentifier, title, abstract, pubDate, keywordSet
def test_processor_extracts_top_metadata(client, model):
    metadata = load_metadata("eml/eml-210.xml")
    sysmeta = load_sysmeta("eml-210-sysmeta.xml")

    processor = EML210Processor(client, model, sysmeta, metadata, [])
    processor.process()
    node_id = "https://dataone.org/datasets/eml-210"

    # Create the alternateIdentifier node
    statement = RDF.Statement(
        RDF.Node(RDF.Uri(node_id)),
        RDF.Node(RDF.Uri("https://schema.org/identifier")),
        RDF.Node("2002-2013_Kling_AON_Imnavait_Chemistry.06"),
    )
    assert model_has_statement(processor.model, statement)
    # Create the title node
    statement = RDF.Statement(
        RDF.Node(RDF.Uri(node_id)),
        RDF.Node(RDF.Uri("https://schema.org/name")),
        RDF.Node("Biogeochemistry data set for Imnavait Creek Weir on the North Slope of Alaska."),
    )
    assert model_has_statement(processor.model, statement)
    # Create the abstract node
    statement = RDF.Statement(
        RDF.Node(RDF.Uri(node_id)),
        RDF.Node(RDF.Uri("https://schema.org/description")),
        RDF.Node("Data file describing the biogeochemistry of samples collected at Imnavait Creek "
                 ",North Slope of Alaska. Sample site descriptors include a unique assigned number "
                 "(sortchem), site, date, time, depth, distance (downstream), elevation, and category. "
                 "Physical measures collected in the field include temperature, conductivity, pH. "
                 "Chemical analysis for the sample include alkalinity; dissolved organic carbon (DOC); "
                 "inorganic and total dissolved nutrients (NH4, PO4, NO3, TDN, TDP); particulate carbon, "
                 "nitrogen, and phosphorus (PC, PN, and PP); cations (Ca, Mg, Na, K); anions (SO4 and Cl); "
                 "silica and oxygen."),
    )
    assert model_has_statement(processor.model, statement)
    # Create the pubDatenode
    statement = RDF.Statement(
        RDF.Node(RDF.Uri(node_id)),
        RDF.Node(RDF.Uri("https://schema.org/datePublished")),
        RDF.Node("2014"),
    )
    assert model_has_statement(processor.model, statement)
    for keyword in ["carbon", "nitrogen", "phosphorus", "ammonium", "total dissolved nitrogen",
                    "alkalinity", "dissolved organic carbon", "carbon dioxide", "methane"]:
        # Create the keywordSet node
        statement = RDF.Statement(
            RDF.Node(RDF.Uri(node_id)),
            RDF.Node(RDF.Uri("https://schema.org/keyword")),
            RDF.Node(keyword),
        )
        assert model_has_statement(processor.model, statement)
