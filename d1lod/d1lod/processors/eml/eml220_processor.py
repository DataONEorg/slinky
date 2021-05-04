import RDF
from urllib.parse import quote_plus as q
import logging

from .eml_processor import EMLProcessor

logger = logging.getLogger(__name__)


class EML220Processor(EMLProcessor):
    def __init__(self, client, model, sysmeta, scimeta, parts):
        super().__init__(client, model, sysmeta, scimeta, parts)

    def process(self):
        logger.debug(f"EML220Processor.process '{self.identifier}'")

        dataset_subject = self.get_dataset_subject()

        # dataset/project/award -> schema:award
        for award in self.scimeta.findall(".//dataset/project/award"):
            funder_name = award.find("./funderName").text
            award_number = award.find("./awardNumber").text
            title = award.find("./title").text

            self.model.append(
                RDF.Statement(
                    dataset_subject,
                    RDF.Node(RDF.Uri("https://schema.org/award")),
                    RDF.Node(f"{funder_name} #{award_number} ({title})"),
                )
            )

        """
        annotations

        The strategy here is to search for each of the places annotations can be
        and then find annotations within those elements. The reason is that we
        need the "id" attribute of the parent element of every annotation and
        ElementTree has funky support for this. Instead, we just start at the
        parent, save the id, and iterate over all child annotations.
        """

        # semantic annotations (dataset, entity, attribute)
        self.process_child_annotations_at(".//dataset")
        self.process_child_annotations_at(
            ".//dataset/otherEntity | .//dataset/dataTable | .//dataset/view | .//dataset/spatialVector | .//dataset/spatailRaster"
        )
        self.process_child_annotations_at(".//dataset/*/attributeList/attribute")

        # top-level annotations
        for annotation in self.scimeta.findall(".//annotations/annotation"):
            id = annotation.attrib["references"]

            for annotation in attribute.findall("annotation"):
                self.model.append(
                    RDF.Statement(
                        RDF.Node(RDF.Uri(f"{dataset_subject.uri}#{q(id)}")),
                        RDF.Node(
                            RDF.Uri(annotation.find("./propertyURI").text.strip())
                        ),
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

    def get_dataset_subject(self):
        return super().get_dataset_subject()
