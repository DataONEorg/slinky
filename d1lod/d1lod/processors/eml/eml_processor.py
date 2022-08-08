import RDF
from urllib.parse import quote_plus as q
import uuid
import logging

from ..processor import Processor
from ..util import (
    element_text,
    is_orcid,
    get_orcid,
    PARTY_TYPE_PERSON,
    PARTY_TYPE_ORGANIZATION,
)
from ...exceptions import ProcessingException
from ...namespaces import NS_SCHEMA, NS_RDF, NS_WD, NS_OBOE

logger = logging.getLogger(__name__)


class EMLProcessor(Processor):
    def __init__(self, client, model, sysmeta, scimeta, parts):
        super().__init__(client, model, sysmeta, scimeta, parts)

    def process(self):
        logger.debug(f"EMLProcessor.process '{self.identifier}'")

        dataset_subject = super().get_dataset_subject()

        # dataset/alternateIdentifier -> schema:identifier
        for alternate_identifier in self.scimeta.findall(
            ".//dataset/alternateIdentifier"
        ):
            self.model.append(
                RDF.Statement(
                    dataset_subject,
                    RDF.Node(RDF.Uri(NS_SCHEMA.identifier)),
                    RDF.Node(alternate_identifier.text.strip()),
                )
            )

        # dataset/title -> schema:name
        for name in self.scimeta.findall(".//dataset/title"):
            self.model.append(
                RDF.Statement(
                    dataset_subject,
                    RDF.Node(RDF.Uri(NS_SCHEMA.name)),
                    RDF.Node(name.text.strip()),
                )
            )

        # dataset/abstract -> schema:description
        for description in self.scimeta.findall(".//dataset/abstract"):
            self.model.append(
                RDF.Statement(
                    dataset_subject,
                    RDF.Node(RDF.Uri(NS_SCHEMA.description)),
                    RDF.Node(element_text(description)),
                )
            )

        # dataset/pubDate -> schema:datePublished
        for pub_date in self.scimeta.findall(".//dataset/pubDate"):
            self.model.append(
                RDF.Statement(
                    dataset_subject,
                    RDF.Node(RDF.Uri(NS_SCHEMA.datePublished)),
                    RDF.Node(pub_date.text.strip()),
                )
            )
        # datset/publisher -> schema:publisher
        self.process_publisher()

        # dataset/creator -> schema:creator
        creators = self.process_creators()

        for creator in creators:
            self.model.append(
                RDF.Statement(
                    dataset_subject,
                    RDF.Node(RDF.Uri(NS_SCHEMA.creator)),
                    creator,
                )
            )

        # dataset/keywordSet -> schema:keywords
        for keyword in self.scimeta.findall(".//dataset/keywordSet/keyword"):
            self.model.append(
                RDF.Statement(
                    dataset_subject,
                    RDF.Node(RDF.Uri(NS_SCHEMA.keyword)),
                    RDF.Node(keyword.text.strip()),
                )
            )

        # schema:variableMeasured
        for attribute in self.scimeta.findall(".//dataset/*/attributeList/attribute"):
            self.process_attribute(attribute)

        # dataset/project/funding -> schema:award
        # See eml220_processor.py for dataset/project/award processing
        for funding in self.scimeta.findall(".//dataset/project/funding"):
            self.model.append(
                RDF.Statement(
                    dataset_subject,
                    RDF.Node(RDF.Uri(NS_SCHEMA.award)),
                    RDF.Node(element_text(funding)),
                )
            )

        # datset/coverage/temporalCoverage -> schema:temporalCoverage
        self.process_temporal_coverage()

        # datset/coverage/spatialCoverage -> schema:spatialCoverage
        self.process_spatial_coverage()

        return super().process()

    def process_creators(self):
        return [
            self.process_party(creator)
            for creator in self.scimeta.findall(".//dataset/creator")
        ]

    def process_party(self, party):
        party_type = self.get_party_type(party)
        if party_type == NS_SCHEMA.Person:
            return self.process_person(party)
        elif party_type == NS_SCHEMA.Organization:
            return self.process_organization(party)
        else:
            logger.error(f"Getting the party type of {element_text(party)} failed")
            raise ProcessingException

    def process_person(self, party):
        person_id = self.get_party_id(party, PARTY_TYPE_PERSON)
        party_subject = RDF.Node(RDF.Uri(person_id))
        person_name = self.get_person_name(party)

        # rdf:type
        self.model.append(
            RDF.Statement(
                party_subject,
                RDF.Node(RDF.Uri(NS_RDF.type)),
                RDF.Node(RDF.Uri(NS_SCHEMA.Person)),
            )
        )

        # schema:name
        self.model.append(
            RDF.Statement(
                party_subject,
                RDF.Node(RDF.Uri(NS_SCHEMA.name)),
                person_name,
            )
        )

        # schema:affiliation
        for organization in party.findall(".//organizationName"):
            affiliation_id = self.get_party_id(party, PARTY_TYPE_ORGANIZATION)
            organization_subject = RDF.Node(RDF.Uri(affiliation_id))

            # schema:affiliation
            self.model.append(
                RDF.Statement(
                    party_subject,
                    RDF.Node(RDF.Uri(NS_SCHEMA.affiliation)),
                    organization_subject,
                )
            )

            # schema:Organization rdf:type
            self.model.append(
                RDF.Statement(
                    organization_subject,
                    RDF.Node(RDF.Uri(NS_RDF.type)),
                    RDF.Node(RDF.Uri(NS_SCHEMA.Organization)),
                )
            )

            # schema:Organization schema:name
            self.model.append(
                RDF.Statement(
                    organization_subject,
                    RDF.Node(RDF.Uri(NS_SCHEMA.name)),
                    organization.text.strip(),
                )
            )

        # schema:email
        for email in party.findall(".//electronicMailAddress"):
            self.model.append(
                RDF.Statement(
                    party_subject,
                    RDF.Node(RDF.Uri(NS_SCHEMA.email)),
                    email.text.strip(),
                )
            )

        # schema:identifier
        for user_id in party.findall(".//userId"):
            self.process_user_id(party_subject, user_id)

        return party_subject

    def process_publisher(self):
        publisher = self.scimeta.find(".//dataset/publisher")

        if publisher is None:
            return

        dataset_subject = self.get_dataset_subject()
        publisher_subject = self.process_party(publisher)

        self.model.append(
            RDF.Statement(
                dataset_subject,
                RDF.Node(RDF.Uri(NS_SCHEMA.publisher)),
                publisher_subject,
            )
        )

    def process_user_id(self, party_subject, user_id):
        """Process the userId portion of a party"""

        # First get the value...
        user_id_text = user_id.text.strip()

        # Use a named node when the userId is an identifier we support,
        # otherwise use a blank node
        # TODO: Support more identifier types
        if is_orcid(user_id_text):
            identifier_node = RDF.Node(
                RDF.Uri(f"https://orcid.org/{get_orcid(user_id_text)}")
            )
        else:
            identifier_node = RDF.Node(blank=user_id_text)

        # schema:identifier
        self.model.append(
            RDF.Statement(
                party_subject,
                RDF.Node(RDF.Uri(NS_SCHEMA.identifier)),
                identifier_node,
            )
        )

        # rdf:type
        self.model.append(
            RDF.Statement(
                identifier_node,
                RDF.Node(RDF.Uri(NS_RDF.type)),
                RDF.Node(RDF.Uri(NS_SCHEMA.PropertyValue)),
            )
        )

        # schema:propertyID
        self.model.append(
            RDF.Statement(
                identifier_node,
                RDF.Node(RDF.Uri(NS_SCHEMA.propertyID)),
                RDF.Node(user_id.attrib["directory"]),
            )
        )

        # schema:value
        if is_orcid(user_id_text):
            self.model.append(
                RDF.Statement(
                    identifier_node,
                    RDF.Node(RDF.Uri(NS_SCHEMA.value)),
                    RDF.Node(get_orcid(user_id_text)),
                )
            )
        else:
            self.model.append(
                RDF.Statement(
                    identifier_node,
                    RDF.Node(RDF.Uri(NS_SCHEMA.value)),
                    RDF.Node(user_id_text),
                )
            )

        # schema:url
        # Only gets added for ORCID.
        # TODO: Expand this to support more of the common identifiers
        if is_orcid(user_id_text):
            self.model.append(
                RDF.Statement(
                    identifier_node,
                    RDF.Node(RDF.Uri(NS_SCHEMA.url)),
                    RDF.Node(f"https://orcid.org/{get_orcid(user_id_text)}"),
                )
            )

    def process_organization(self, party):
        org_id = self.get_party_id(party, PARTY_TYPE_ORGANIZATION)
        party_subject = RDF.Node(RDF.Uri(org_id))
        org_name = self.get_organization_name(party)

        # rdf:type
        self.model.append(
            RDF.Statement(
                party_subject,
                RDF.Node(RDF.Uri(NS_RDF.type)),
                RDF.Node(RDF.Uri(NS_SCHEMA.Organization)),
            )
        )

        # schema:name
        self.model.append(
            RDF.Statement(
                party_subject,
                RDF.Node(RDF.Uri(NS_SCHEMA.name)),
                org_name,
            )
        )

        # schema:email
        for email in party.findall(".//electronicMailAddress"):
            self.model.append(
                RDF.Statement(
                    party_subject,
                    RDF.Node(RDF.Uri(NS_SCHEMA.email)),
                    email.text.strip(),
                )
            )

        # schema:identifier
        for user_id in party.findall(".//userId"):
            self.process_user_id(party_subject, user_id)

        return party_subject

    def process_temporal_coverage(self):
        dataset_subject = self.get_dataset_subject()

        for temporal_coverage in self.scimeta.findall(
            ".//dataset/coverage/temporalCoverage"
        ):
            for single_date_time in temporal_coverage.findall(".//singleDateTime"):
                calendar_date = single_date_time.find(".//calendarDate")

                if calendar_date is None:
                    raise ProcessingException(
                        "Found a document without a calendarDate. This might be an alternativeTimeScale document"
                    )

                self.model.append(
                    RDF.Statement(
                        dataset_subject,
                        RDF.Node(RDF.Uri(NS_SCHEMA.temporalCoverage)),
                        RDF.Node(calendar_date.text.strip()),
                    )
                )

            for range_of_dates in temporal_coverage.findall(".//rangeOfDates"):
                beginDate = range_of_dates.find("./beginDate/calendarDate")
                endDate = range_of_dates.find("./endDate/calendarDate")

                self.model.append(
                    RDF.Statement(
                        dataset_subject,
                        RDF.Node(RDF.Uri(NS_SCHEMA.temporalCoverage)),
                        RDF.Node(f"{beginDate.text.strip()}/{endDate.text.strip()}"),
                    )
                )

    def process_attribute(self, attribute):
        dataset_subject = self.get_dataset_subject()

        property_value_bnode = RDF.Node(blank=str(uuid.uuid4()))

        self.model.append(
            RDF.Statement(
                dataset_subject,
                RDF.Node(RDF.Uri(NS_SCHEMA.variableMeasured)),
                property_value_bnode,
            )
        )

        # rdf:type
        self.model.append(
            RDF.Statement(
                property_value_bnode,
                RDF.Node(RDF.Uri(NS_RDF.type)),
                RDF.Node(RDF.Uri(NS_SCHEMA.PropertyValue)),
            )
        )

        # attributeName -> schema:name
        for name in attribute.findall("./attributeName"):
            self.model.append(
                RDF.Statement(
                    property_value_bnode,
                    RDF.Node(RDF.Uri(NS_SCHEMA.name)),
                    RDF.Node(name.text.strip()),
                )
            )

        # attributeLabel -> schema:alternateName
        for label in attribute.findall("./attributeLabel"):
            self.model.append(
                RDF.Statement(
                    property_value_bnode,
                    RDF.Node(RDF.Uri(NS_SCHEMA.alternateName)),
                    RDF.Node(label.text.strip()),
                )
            )

        # attributeDefinition -> schema:description
        for description in attribute.findall("./attributeDefinition"):
            self.model.append(
                RDF.Statement(
                    property_value_bnode,
                    RDF.Node(RDF.Uri(NS_SCHEMA.description)),
                    RDF.Node(description.text.strip()),
                )
            )
        # standardUnit | customUnit -> schema:unitText
        for unit in attribute.findall(".//standardUnit") + attribute.findall(
            ".//customUnit"
        ):
            self.model.append(
                RDF.Statement(
                    property_value_bnode,
                    RDF.Node(RDF.Uri(NS_SCHEMA.unitText)),
                    RDF.Node(unit.text.strip()),
                )
            )

        # measurementType -> propertyID
        # schema:description
        for annotation in attribute.findall("./annotation"):
            propertyURI = annotation.find("./propertyURI")
            valueURI = annotation.find("./valueURI")

            if (
                propertyURI is None
                or propertyURI.text.strip() != NS_OBOE.containsMeasurementsOfType
            ):
                continue

            self.model.append(
                RDF.Statement(
                    property_value_bnode,
                    RDF.Node(RDF.Uri(NS_SCHEMA.propertyID)),
                    RDF.Node(RDF.Uri(valueURI.text.strip())),
                )
            )

    def process_spatial_coverage(self):
        dataset_subject = self.get_dataset_subject()

        for geographic_coverage in self.scimeta.findall(
            ".//dataset/coverage/geographicCoverage"
        ):
            descriptions = geographic_coverage.findall(".//geographicDescription")
            bounding_coordinates = geographic_coverage.findall(".//boundingCoordinates")

            if len(bounding_coordinates) != 1:
                raise ProcessingException(
                    "Encountered a spatialCoverage without boundingCoordinates"
                )

            # Set up blank nodes ahead of time
            place_bnode = RDF.Node(blank=str(uuid.uuid4()))
            geo_bnode = RDF.Node(blank=str(uuid.uuid4()))
            additional_property_wkt_bnode = RDF.Node(blank=str(uuid.uuid4()))
            additional_property_crs_bnode = RDF.Node(blank=str(uuid.uuid4()))

            # schema:description
            for description in descriptions:
                self.model.append(
                    RDF.Statement(
                        place_bnode,
                        RDF.Node(RDF.Uri(NS_SCHEMA.description)),
                        RDF.Node(description.text.strip()),
                    )
                )

            # Get bounding box
            north = (
                bounding_coordinates[0]
                .findall(".//northBoundingCoordinate")[0]
                .text.strip()
            )
            east = (
                bounding_coordinates[0]
                .findall(".//eastBoundingCoordinate")[0]
                .text.strip()
            )
            south = (
                bounding_coordinates[0]
                .findall(".//southBoundingCoordinate")[0]
                .text.strip()
            )
            west = (
                bounding_coordinates[0]
                .findall(".//westBoundingCoordinate")[0]
                .text.strip()
            )

            # schema:spatialCoverage
            self.model.append(
                RDF.Statement(
                    dataset_subject,
                    RDF.Node(RDF.Uri(NS_SCHEMA.spatialCoverage)),
                    place_bnode,
                )
            )

            # rdf:type
            self.model.append(
                RDF.Statement(
                    place_bnode,
                    RDF.Node(RDF.Uri(NS_RDF.type)),
                    RDF.Node(RDF.Uri(NS_SCHEMA.Place)),
                )
            )

            # Place -> schema:geo
            self.model.append(
                RDF.Statement(
                    place_bnode,
                    RDF.Node(RDF.Uri(NS_SCHEMA.geo)),
                    geo_bnode,
                )
            )

            if north == south and east == west:
                # geo -> rdf:type
                self.model.append(
                    RDF.Statement(
                        geo_bnode,
                        RDF.Node(RDF.Uri(NS_RDF.type)),
                        RDF.Node(RDF.Uri(NS_SCHEMA.GeoCoordinates)),
                    )
                )

                # geo -> schema:latitude
                self.model.append(
                    RDF.Statement(
                        geo_bnode,
                        RDF.Node(RDF.Uri(NS_SCHEMA.latitude)),
                        RDF.Node(f"{north}"),
                    )
                )

                # geo -> schema:longitude
                self.model.append(
                    RDF.Statement(
                        geo_bnode,
                        RDF.Node(RDF.Uri(NS_SCHEMA.longitude)),
                        RDF.Node(f"{east}"),
                    )
                )

                # schema:additionalProperty
                self.model.append(
                    RDF.Statement(
                        place_bnode,
                        RDF.Node(RDF.Uri(NS_SCHEMA.additionalProperty)),
                        additional_property_wkt_bnode,
                    )
                )

                # rdf:type
                self.model.append(
                    RDF.Statement(
                        additional_property_wkt_bnode,
                        RDF.Node(RDF.Uri(NS_RDF.type)),
                        RDF.Node(RDF.Uri(NS_SCHEMA.PropertyValue)),
                    )
                )

                # schema:propertyID
                self.model.append(
                    RDF.Statement(
                        additional_property_wkt_bnode,
                        RDF.Node(RDF.Uri(NS_SCHEMA.propertyID)),
                        RDF.Node(RDF.Uri(NS_WD.Q4018860)),
                    )
                )

                # schema:value
                self.model.append(
                    RDF.Statement(
                        additional_property_wkt_bnode,
                        RDF.Node(RDF.Uri(NS_SCHEMA.name)),
                        RDF.Node("Well-Known Text (WKT) representation of geometry"),
                    )
                )

                # schema:url
                self.model.append(
                    RDF.Statement(
                        additional_property_wkt_bnode,
                        RDF.Node(RDF.Uri(NS_SCHEMA.value)),
                        RDF.Node(f"POINT ({west} {north})"),
                    )
                )
            else:
                # geo -> rdf:type
                self.model.append(
                    RDF.Statement(
                        geo_bnode,
                        RDF.Node(RDF.Uri(NS_RDF.type)),
                        RDF.Node(RDF.Uri(NS_SCHEMA.GeoShape)),
                    )
                )

                # geo -> schema:box
                self.model.append(
                    RDF.Statement(
                        geo_bnode,
                        RDF.Node(RDF.Uri(NS_SCHEMA.box)),
                        RDF.Node(f"{north},{east} {south},{west}"),
                    )
                )

                # schema:additionalProperty
                self.model.append(
                    RDF.Statement(
                        place_bnode,
                        RDF.Node(RDF.Uri(NS_SCHEMA.additionalProperty)),
                        additional_property_wkt_bnode,
                    )
                )

                # rdf:type
                self.model.append(
                    RDF.Statement(
                        additional_property_wkt_bnode,
                        RDF.Node(RDF.Uri(NS_RDF.type)),
                        RDF.Node(RDF.Uri(NS_SCHEMA.PropertyValue)),
                    )
                )

                # schema:propertyID
                self.model.append(
                    RDF.Statement(
                        additional_property_wkt_bnode,
                        RDF.Node(RDF.Uri(NS_SCHEMA.propertyID)),
                        RDF.Node(RDF.Uri(NS_WD.Q4018860)),
                    )
                )

                # schema:value
                self.model.append(
                    RDF.Statement(
                        additional_property_wkt_bnode,
                        RDF.Node(RDF.Uri(NS_SCHEMA.name)),
                        RDF.Node("Well-Known Text (WKT) representation of geometry"),
                    )
                )

                # schema:url
                self.model.append(
                    RDF.Statement(
                        additional_property_wkt_bnode,
                        RDF.Node(RDF.Uri(NS_SCHEMA.value)),
                        RDF.Node(
                            f"POLYGON (({west} {north}, {east} {north}, {east} {south}, {west} {south}, {west} {north}))"
                        ),
                    )
                )

            # schema:additionalProperty
            self.model.append(
                RDF.Statement(
                    place_bnode,
                    RDF.Node(RDF.Uri(NS_SCHEMA.additionalProperty)),
                    additional_property_crs_bnode,
                )
            )

            # rdf:type
            self.model.append(
                RDF.Statement(
                    additional_property_crs_bnode,
                    RDF.Node(RDF.Uri(NS_RDF.type)),
                    RDF.Node(RDF.Uri(NS_SCHEMA.PropertyValue)),
                )
            )

            # schema:propertyID
            self.model.append(
                RDF.Statement(
                    additional_property_crs_bnode,
                    RDF.Node(RDF.Uri(NS_SCHEMA.propertyID)),
                    RDF.Node(RDF.Uri(NS_WD.Q4018860)),
                )
            )

            # schema:value
            self.model.append(
                RDF.Statement(
                    additional_property_crs_bnode,
                    RDF.Node(RDF.Uri(NS_SCHEMA.name)),
                    RDF.Node("Spatial Reference System"),
                )
            )

            # schema:url
            self.model.append(
                RDF.Statement(
                    additional_property_crs_bnode,
                    RDF.Node(RDF.Uri(NS_SCHEMA.value)),
                    RDF.Node("http://www.opengis.net/def/crs/OGC/1.3/CRS84"),
                )
            )

    def get_dataset_subject(self):
        return super().get_dataset_subject()

    def get_party_id(self, party, party_type):
        logger.debug(f"get_party_id for '{element_text(party)}' of type '{party_type}'")

        party_id = self.lookup_party_id(party, party_type)

        if party_id is None:
            logger.info(
                f"get_party_id: Creating new ID for party '{element_text(party)}' instead of re-using one"
            )

            new_uuid = f"urn:uuid:{uuid.uuid4()}"

            if party_type == PARTY_TYPE_PERSON:
                return f"https://dataone.org/people/{q(new_uuid)}"
            elif party_type == PARTY_TYPE_ORGANIZATION:
                return f"https://dataone.org/organizations/{q(new_uuid)}"

        logger.info(f"get_party_id: Matched party {element_text(party)} to {party_id}")

        return party_id

    def get_party_type(self, party):
        if party.find("./individualName") is not None:
            return NS_SCHEMA.Person
        elif party.find("./organizationName") is not None:
            return NS_SCHEMA.Organization
        else:
            return None

    def get_person_name(self, party):
        given = [el.text.strip() for el in party.findall(".//individualName/givenName")]
        sur = [el.text.strip() for el in party.findall(".//individualName/surName")]

        return f"{' '.join(given)} {' '.join(sur)}".strip()

    def get_organization_name(self, party):
        return "".join([el.text.strip() for el in party.findall(".//organizationName")])

    def identifier_statement_exists(self, subject, value: str):
        query_text = f"""SELECT ?identifier
        WHERE {{
            <{str(subject)}> <http://schema.org/identifier> ?identifier .
            ?identifier <http://schema.org/value> "{value}"
        }}"""

        query = RDF.Query(query_text)
        results = query.execute(self.model)

        if len([statement for statement in results]) > 0:
            return True

        return False

    def lookup_party_id(self, party, party_type):
        if party_type == PARTY_TYPE_PERSON:
            last_name = party.find("./individualName/surName")
            email = party.find("./electronicMailAddress")

            if last_name is None or email is None:
                return None

            return self.lookup_person(
                last_name.text.strip(),
                email.text.strip(),
            )
        elif party_type == PARTY_TYPE_ORGANIZATION:
            org_name = party.find("./organizationName")

            if org_name is None:
                return None

            return self.lookup_organization(org_name.text.strip())
        else:
            raise ProcessingException(
                f"get_party_id called with invalid type of {party_type}"
            )

    def lookup_person(self, last_name, email):
        return super().lookup_person(last_name, email)

    def lookup_organization(self, name):
        return super().lookup_organization(name)
