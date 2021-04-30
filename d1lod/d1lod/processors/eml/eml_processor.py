import logging
import RDF
from urllib.parse import quote_plus as q
from ..processor import Processor

logger = logging.getLogger(__name__)


class EMLProcessor(Processor):
    def __init__(self, model, sysmeta, scimeta, parts):
        super().__init__(model, sysmeta, scimeta, parts)

    def process(self):
        logger.debug("EMLProcessor.process")
        dataset_subject = RDF.Node(
            RDF.Uri(
                "https://dataone.org/datasets/{}".format(
                    q(self.sysmeta.identifier.value())
                )
            )
        )

        self.model.append(
            RDF.Statement(
                dataset_subject,
                RDF.Node(RDF.Uri("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")),
                RDF.Node(RDF.Uri("https://schema.org/Dataset")),
            )
        )

        self.model.append(
            RDF.Statement(
                dataset_subject,
                RDF.Node(RDF.Uri("https://schema.org/identifier")),
                RDF.Node(self.sysmeta.identifier.value()),
            )
        )

        for name in self.scimeta.findall(".//dataset/title"):
            self.model.append(
                RDF.Statement(
                    dataset_subject,
                    RDF.Node(RDF.Uri("https://schema.org/name")),
                    RDF.Node(name.text),
                )
            )

        for description in self.scimeta.findall(".//dataset/abstract"):
            self.model.append(
                RDF.Statement(
                    dataset_subject,
                    RDF.Node(RDF.Uri("https://schema.org/description")),
                    RDF.Node(
                        "".join([item for item in description.itertext()]).strip()
                    ),
                )
            )

        self.process_parts()

        return self.model

    def process_parts(self):
        super().process_parts()
