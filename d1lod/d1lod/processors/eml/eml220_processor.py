import RDF
from urllib.parse import quote_plus as q
import logging

from .eml_processor import EMLProcessor

logger = logging.getLogger(__name__)


class EML220Processor(EMLProcessor):
    """
    A dataset processor for EML 2.2.0. This processor handles changes to the structured funding
    and supports annotations.
    """

    def __init__(self, client, model, sysmeta, scimeta, parts):
        super().__init__(client, model, sysmeta, scimeta, parts)

    def process(self):
        logger.debug(f"EML220Processor.process '{self.identifier}'")

        dataset_subject = self.get_dataset_subject()

        # dataset/project/award -> schema:award
        for award in self.scimeta.findall(".//dataset/project/award"):
            self.process_award(dataset_subject, award)

        """
        annotations

        The strategy here is to search for each of the places annotations can be
        and then find annotations within those elements. The reason is that we
        need the "id" attribute of the parent element of every annotation and
        ElementTree has funky support for this. Instead, we just start at the
        parent, save the id, and iterate over all child annotations.
        """

        # dataset-level annotations
        self.process_child_annotations_at(".//dataset")

        # entity-level annotations
        # ElementTree doesn't support | in XPaths so we do this...
        self.process_child_annotations_at(".//dataset/otherEntity")
        self.process_child_annotations_at(".//dataset/dataTable")
        self.process_child_annotations_at(".//dataset/view")
        self.process_child_annotations_at(".//dataset/spatialVector")
        self.process_child_annotations_at(".//dataset/spatailRaster")

        # attribute-level annotations
        self.process_child_annotations_at(".//dataset/*/attributeList/attribute")

        # top-level annotations
        for annotation in self.scimeta.findall(".//annotations/annotation"):
            id = annotation.attrib["references"]

            self.model.append(
                RDF.Statement(
                    RDF.Node(RDF.Uri(f"{dataset_subject.uri}#{q(id)}")),
                    RDF.Node(RDF.Uri(annotation.find("./propertyURI").text.strip())),
                    RDF.Node(RDF.Uri(annotation.find("./valueURI").text.strip())),
                )
            )

        # additionalMetadata annotations
        for additional_metadata in self.scimeta.findall(".//additionalMetadata"):
            if additional_metadata.find("./metadata/annotation") is None:
                continue

            id = additional_metadata.find("./describes").text

            for annotation in additional_metadata.findall("./metadata/annotation"):
                self.model.append(
                    RDF.Statement(
                        RDF.Node(RDF.Uri(f"{dataset_subject.uri}#{q(id)}")),
                        RDF.Node(
                            RDF.Uri(annotation.find("./propertyURI").text.strip())
                        ),
                        RDF.Node(RDF.Uri(annotation.find("./valueURI").text.strip())),
                    )
                )

        return super().process()

    def process_child_annotations_at(self, xpath_text):
        """Annotations which need a parent"""

        dataset_subject = self.get_dataset_subject()

        for element in self.scimeta.findall(xpath_text):
            for annotation in element.findall("./annotation"):
                id = element.attrib["id"]

                self.model.append(
                    RDF.Statement(
                        RDF.Node(RDF.Uri(f"{dataset_subject.uri}#{q(id)}")),
                        RDF.Node(
                            RDF.Uri(annotation.find("./propertyURI").text.strip())
                        ),
                        RDF.Node(RDF.Uri(annotation.find("./valueURI").text.strip())),
                    )
                )

    def process_award(self, dataset_subject, award):
        """Process an award

        XML:
        <award>
            <funderName>National Science Foundation</funderName>
            <funderIdentifier>https://doi.org/10.13039/00000001</funderIdentifier>
            <awardNumber>1546024</awardNumber>
            <title>Scientia Arctica: A Knowledge Archive for Discovery and Reproducible Science in the Arctic</title>
            <awardUrl>https://www.nsf.gov/awardsearch/showAward?AWD_ID=1546024</awardUrl>
        </award>

        JSON-LD:
        {
            "@id": "https://www.nsf.gov/awardsearch/showAward?AWD_ID=1604105",
            "@type": "MonetaryGrant",
            "identifier": "1604105",
            "name": "Collaborative Research: Nutritional Landscapes of Arctic Caribou: Observations, Experiments, and Models Provide Process-Level Understanding of Forage Traits and Trajectories",
            "url": "https://www.nsf.gov/awardsearch/showAward?AWD_ID=1604105",
            "funder": {
                "@id": "http://dx.doi.org/10.13039/100000001",
                "@type": "Organization",
                "name": "National Science Foundation",
                "identifier": [
                "http://dx.doi.org/10.13039/100000001",
                "https://ror.org/021nxhr62"
                ]
            }
        }

        """

        funderName = award.find("./funderName").text  # 1:1
        awardNumber = award.find("./awardNumber").text  # 1:1
        funderIdentifier = award.findall("./funderIdentifier")  # 0-∞
        title = award.find("./title").text  # 1:1
        awardUrl = award.find("./awardUrl")  # 0:1

        # Determine whether to use a blank node or not based upon whether the
        # award has an awardUrl or not
        if awardUrl is not None:
            award_node = RDF.Node(RDF.Uri(awardUrl.text))
        else:
            award_node = RDF.Node(blank="award")

        # dataset -> award
        self.model.append(
            RDF.Statement(
                dataset_subject,
                RDF.Node(RDF.Uri("https://schema.org/award")),
                award_node,
            )
        )

        # @type
        self.model.append(
            RDF.Statement(
                award_node,
                RDF.Node(RDF.Uri("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")),
                RDF.Node(RDF.Uri("https://schema.org/MonetaryGrant")),
            )
        )

        # title -> name
        self.model.append(
            RDF.Statement(
                award_node,
                RDF.Node(RDF.Uri("https://schema.org/name")),
                title,
            )
        )

        # awardNumber -> identifier
        self.model.append(
            RDF.Statement(
                award_node,
                RDF.Node(RDF.Uri("https://schema.org/identifier")),
                awardNumber,
            )
        )

        # awardUrl (0-1) -> url
        if awardUrl is not None:
            self.model.append(
                RDF.Statement(
                    award_node,
                    RDF.Node(RDF.Uri("https://schema.org/url")),
                    awardUrl.text,
                )
            )

        # funder blank node
        # Uses the first funderIdentifier as the URI and puts all values in
        # as 'schema:identifier' triples
        if len(funderIdentifier) > 0:
            funder_node = RDF.Node(RDF.Uri(funderIdentifier[0].text))
        else:
            funder_node = RDF.Node(blank="funder")

        # award node -> funder node
        self.model.append(
            RDF.Statement(
                award_node,
                RDF.Node(RDF.Uri("https://schema.org/funder")),
                funder_node,
            )
        )

        # @type
        self.model.append(
            RDF.Statement(
                funder_node,
                RDF.Node(RDF.Uri("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")),
                RDF.Node(RDF.Uri("https://schema.org/Organization")),
            )
        )

        # funderName -> name
        self.model.append(
            RDF.Statement(
                funder_node,
                RDF.Node(RDF.Uri("https://schema.org/name")),
                funderName,
            )
        )

        # funderIdentifier (0-∞) -> identifier
        for identifier in funderIdentifier:
            self.model.append(
                RDF.Statement(
                    funder_node,
                    RDF.Node(RDF.Uri("https://schema.org/identifier")),
                    identifier.text,
                )
            )

    def get_dataset_subject(self):
        return super().get_dataset_subject()
