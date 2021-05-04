from urllib.parse import quote_plus as q
import RDF
import uuid
import logging

from .util import get_doi, is_doi
from ..exceptions import ProcessingException

logger = logging.getLogger(__name__)


class Processor:
    def __init__(self, client, model, sysmeta, scimeta, parts):
        self.client = client
        self.model = model
        self.sysmeta = sysmeta
        self.identifier = sysmeta.identifier.value()
        self.scimeta = scimeta
        self.parts = parts

    def process(self):
        logger.debug(f"Processor.process '{self.identifier}'")
        dataset_subject = self.get_dataset_subject()

        # rdf:type
        self.model.append(
            RDF.Statement(
                dataset_subject,
                RDF.Node(RDF.Uri("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")),
                RDF.Node(RDF.Uri("https://schema.org/Dataset")),
            )
        )

        # schema:identifier
        self.process_identifier()

        # schema:dateModified
        self.model.append(
            RDF.Statement(
                dataset_subject,
                RDF.Node(RDF.Uri("https://schema.org/dateModified")),
                RDF.Node(
                    self.sysmeta.dateSysMetadataModified.strftime(
                        "%Y-%m-%dT%H:%M:%S.%fZ"
                    )
                ),
            )
        )
        # schema:datePublished
        self.model.append(
            RDF.Statement(
                dataset_subject,
                RDF.Node(RDF.Uri("https://schema.org/datePublished")),
                RDF.Node(self.sysmeta.dateUploaded.strftime("%Y-%m-%dT%H:%M:%S.%fZ")),
            )
        )

        # schema:url
        self.model.append(
            RDF.Statement(
                dataset_subject,
                RDF.Node(RDF.Uri("https://schema.org/url")),
                RDF.Node(f"https://dataone.org/datasets/{q(self.identifier)}"),
            )
        )

        # schema:sameAs
        if is_doi(self.identifier):
            doi = get_doi(self.identifier)

            self.model.append(
                RDF.Statement(
                    dataset_subject,
                    RDF.Node(RDF.Uri("https://schema.org/sameAs")),
                    RDF.Node(f"https://doi.org/{q(doi)}"),
                )
            )

        # schema:wasRevisionOf
        obsoletes = self.sysmeta.obsoletes.value()

        if obsoletes:
            self.model.append(
                RDF.Statement(
                    dataset_subject,
                    RDF.Node(RDF.Uri("https://schema.org/wasRevisionOf")),
                    RDF.Node(f"https://dataone.org/datasets/{q(obsoletes)}"),
                )
            )

        # schema:schemaVersion
        self.model.append(
            RDF.Statement(
                dataset_subject,
                RDF.Node(RDF.Uri("https://schema.org/schemaVersion")),
                RDF.Node(self.sysmeta.formatId),
            )
        )

        # schema:isAccessibleForFree
        if self.is_accessible_for_free():
            self.model.append(
                RDF.Statement(
                    dataset_subject,
                    RDF.Node(RDF.Uri("https://schema.org/isAccessibleForFree")),
                    RDF.Node("true"),
                )
            )

        # checksum
        self.model.append(
            RDF.Statement(
                dataset_subject,
                RDF.Node(RDF.Uri("http://spdx.org/rdf/terms#Checksum")),
                RDF.Node(self.sysmeta.checksum.value()),
            )
        )

        # checksumAlgorithm
        self.model.append(
            RDF.Statement(
                dataset_subject,
                RDF.Node(RDF.Uri("http://spdx.org/rdf/terms#ChecksumAlgorithm")),
                RDF.Node(self.sysmeta.checksum.algorithm),
            )
        )

        # schema:byteSize
        if self.is_accessible_for_free():
            total_size = self.sysmeta.size + sum([part.size for part in self.parts])

            self.model.append(
                RDF.Statement(
                    dataset_subject,
                    RDF.Node(RDF.Uri("https://schema.org/byteSize")),
                    RDF.Node(
                        literal=str(total_size),
                        datatype=RDF.Uri("http://www.w3.org/2001/XMLSchema#integer"),
                    ),
                )
            )

        self.process_parts()

        return self.model

    def process_identifier(self):
        dataset_subject = self.get_dataset_subject()

        if is_doi(self.identifier):
            identifier_bnode = RDF.Node(blank=q(str(uuid.uuid4())))

            # rdf:type
            self.model.append(
                RDF.Statement(
                    dataset_subject,
                    RDF.Node(RDF.Uri("https://schema.org/identifier")),
                    identifier_bnode,
                )
            )

            # rdf:type
            self.model.append(
                RDF.Statement(
                    identifier_bnode,
                    RDF.Node(
                        RDF.Uri("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
                    ),
                    RDF.Node(RDF.Uri("https://schema.org/PropertyValue")),
                )
            )

            # schema:propertyID
            self.model.append(
                RDF.Statement(
                    identifier_bnode,
                    RDF.Node(RDF.Uri("https://schema.org/propertyID")),
                    RDF.Node("https://registry.identifiers.org/registry/doi"),
                )
            )

            # schema:value
            self.model.append(
                RDF.Statement(
                    identifier_bnode,
                    RDF.Node(RDF.Uri("https://schema.org/value")),
                    RDF.Node(get_doi(self.identifier)),
                )
            )

            # schema:url
            self.model.append(
                RDF.Statement(
                    identifier_bnode,
                    RDF.Node(RDF.Uri("https://schema.org/url")),
                    RDF.Node(f"https://doi.org/{q(self.identifier)}"),
                )
            )
        else:
            self.model.append(
                RDF.Statement(
                    dataset_subject,
                    RDF.Node(RDF.Uri("https://schema.org/identifier")),
                    RDF.Node(self.identifier),
                )
            )

    def process_parts(self):
        for part in self.parts:
            # Skip self
            if part.identifier.value() == self.identifier:
                logger.debug(
                    "Skipping part with identifier {} because it's the same as the dataset identifier {}".format(
                        part.identifier.value(), self.identifier
                    )
                )
                continue

            # Skip child packages
            if part.formatId == "http://www.openarchives.org/ore/terms":
                logger.warn(
                    "Skipping {} because it's a child resource map".format(
                        part.identifier.value()
                    )
                )

                continue

            part_subject = RDF.Node(
                RDF.Uri(
                    "https://dataone.org/datasets/{}".format(q(part.identifier.value()))
                )
            )

            # rdf:type
            self.model.append(
                RDF.Statement(
                    part_subject,
                    RDF.Node(
                        RDF.Uri("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
                    ),
                    RDF.Node(RDF.Uri("https://schema.org/DataDownload")),
                )
            )

            # identifier
            self.model.append(
                RDF.Statement(
                    part_subject,
                    RDF.Node(RDF.Uri("https://schema.org/identifier")),
                    RDF.Node(
                        f"https://dataone.org/datasets/{q(part.identifier.value())}"
                    ),
                )
            )

            # schema:contentUrl
            self.model.append(
                RDF.Statement(
                    part_subject,
                    RDF.Node(RDF.Uri("https://schema.org/contentUrl")),
                    RDF.Node(
                        f"https://search.dataone.org/cn/v2/resolve/{q(part.identifier.value())}"
                    ),
                )
            )

            # schema:encodingFormat
            self.model.append(
                RDF.Statement(
                    part_subject,
                    RDF.Node(RDF.Uri("https://schema.org/encodingFormat")),
                    RDF.Node(part.formatId),
                )
            )

            # schema:dateModified
            self.model.append(
                RDF.Statement(
                    part_subject,
                    RDF.Node(RDF.Uri("https://schema.org/dateModified")),
                    RDF.Node(
                        part.dateSysMetadataModified.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                    ),
                )
            )

            # schema:datePublished
            self.model.append(
                RDF.Statement(
                    part_subject,
                    RDF.Node(RDF.Uri("https://schema.org/datePublished")),
                    RDF.Node(part.dateUploaded.strftime("%Y-%m-%dT%H:%M:%S.%fZ")),
                )
            )

            # schema:byteSize
            self.model.append(
                RDF.Statement(
                    part_subject,
                    RDF.Node(RDF.Uri("https://schema.org/byteSize")),
                    RDF.Node(
                        literal=str(part.size),
                        datatype=RDF.Uri("http://www.w3.org/2001/XMLSchema#integer"),
                    ),
                )
            )

            # schema:name
            self.model.append(
                RDF.Statement(
                    part_subject,
                    RDF.Node(RDF.Uri("https://schema.org/name")),
                    RDF.Node(part.fileName),
                )
            )

            # checksum
            self.model.append(
                RDF.Statement(
                    part_subject,
                    RDF.Node(RDF.Uri("http://spdx.org/rdf/terms#Checksum")),
                    RDF.Node(part.checksum.value()),
                )
            )

            # checksumAlgorithm
            self.model.append(
                RDF.Statement(
                    part_subject,
                    RDF.Node(RDF.Uri("http://spdx.org/rdf/terms#ChecksumAlgorithm")),
                    RDF.Node(part.checksum.algorithm),
                )
            )

    # def lookup_person_in_store(self, last_name, email):
    #     pass

    # def lookup_person_in_model(self, last_name, email):
    #     pass

    def lookup_person(self, last_name, email):
        logger.debug(
            f"Looking up person with last name '{last_name}' and email '{email}'"
        )

        # Generate query
        query = f"""select ?s where
            {{
                ?s <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <https://schema.org/Person> .
                ?s <https://schema.org/name> ?name .
                ?s <https://schema.org/email> ?email .
                FILTER regex(str(?name), "{last_name}") .
                FILTER regex(str(?email), "{email}") .
            }}"""

        # Query the entire store first
        response = self.client.store.query(query)

        if len(response) > 0:
            subject = response[0]["s"]

            logger.debug(
                f"Found match for person with last name of '{last_name}' and email of '{email}': {subject}"
            )

            return str(subject)

        # Query the local model as a fallback
        local_response = RDF.Query(query)
        results = local_response.execute(self.model)

        for result in results:
            subject = str(result["s"])

            logger.debug(
                f"Found match for person with last name of '{last_name}' and email of '{email}: {subject}'"
            )

            return str(subject)

        logger.debug(
            f"No lookup match found for a person with last name '{last_name}' and email '{email}'"
        )

        return None

    def lookup_organization(self, name):
        logger.debug(f"Looking up organization '{name}'")

        # Generate query
        query = f"""select ?s where
            {{
                ?s <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <https://schema.org/Organization> .
                ?s <https://schema.org/name> ?name .
                FILTER regex(str(?name), "{name}") .
            }}"""

        # Query the entire store first
        response = self.client.store.query(query)

        if len(response) > 0:
            logger.debug(f"Found match for organization with name of '{name}'")

            return str(response[0]["s"])

        # Query the local model as a fallback
        local_response = RDF.Query(query)
        results = local_response.execute(self.model)

        for result in results:
            subject = str(result["s"])

            logger.debug(
                f"Found match for organization with name '{name}' of '{subject}'"
            )

            return subject

        # We didn't find any results
        logger.debug(f"No lookup match found for an organization with name '{name}'")

        return None

    def get_dataset_subject(self):
        return RDF.Node(
            RDF.Uri("https://dataone.org/datasets/{}".format(q(self.identifier)))
        )

    def is_accessible_for_free(self):
        rules = [rule for rule in self.sysmeta.accessPolicy.allow]

        for rule in rules:
            subject = rule.subject[0].value()

            if subject != "public":
                continue

            permissions = [p for p in rule.permission]

            if "read" in permissions:
                return True

        return False
