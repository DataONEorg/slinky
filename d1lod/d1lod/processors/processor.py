import logging
from urllib.parse import quote_plus as q
import RDF

logger = logging.getLogger(__name__)


class Processor:
    def __init__(self, model, sysmeta, scimeta, parts):
        self.model = model
        self.sysmeta = sysmeta
        self.scimeta = scimeta
        self.parts = parts

    def process_parts(self):
        for part in self.parts:
            # Skip self
            if part.identifier.value() == self.sysmeta.identifier.value():
                logger.debug(
                    "Skipping part with identifier {} because it's the same as the dataset identifier {}".format(
                        part.identifier.value(), self.sysmeta.identifier.value()
                    )
                )
                continue

            part_subject = RDF.Node(
                RDF.Uri(
                    "https://dataone.org/datasets/{}".format(q(part.identifier.value()))
                )
            )

            self.model.append(
                RDF.Statement(
                    part_subject,
                    RDF.Node(
                        RDF.Uri("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
                    ),
                    RDF.Node(RDF.Uri("https://schema.org/DataDownload")),
                )
            )

            self.model.append(
                RDF.Statement(
                    part_subject,
                    RDF.Node(RDF.Uri("https:schema.org/identifier")),
                    RDF.Node(part.identifier.value()),
                )
            )
