import RDF
from urllib.parse import quote_plus as q
import uuid
import logging

from ..processor import Processor
from ..util import (
    element_text,
    PARTY_TYPE_PERSON,
    PARTY_TYPE_ORGANIZATION,
)
from ...exceptions import ProcessingException

logger = logging.getLogger(__name__)

ISO_CREATOR_ROLES = ["owner", "originator", "author", "principalInvestigator"]
NS_MAP = {
    "gmd": "http://www.isotc211.org/2005/gmd",
    "gco": "http://www.isotc211.org/2005/gco",
    "gml": "http://www.opengis.net/gml/3.2",
}


class ISOProcessor(Processor):
    def __init__(self, client, model, sysmeta, scimeta, parts):
        super().__init__(client, model, sysmeta, scimeta, parts)

    def lookup_party_id(self, party, party_type):
        if party_type == PARTY_TYPE_PERSON:
            name = party.find("./gmd:individualName/gco:CharacterString", NS_MAP)
            email = party.find(
                "./gmd:contactInfo/gmd:CI_Contact/gmd:address/gmd:CI_Address/gmd:electronicMailAddress/gco:CharacterString",
                NS_MAP,
            )

            if name is None or email is None:
                return None

            return self.lookup_person(
                name.text.strip(),
                email.text.strip(),
            )
        elif party_type == PARTY_TYPE_ORGANIZATION:
            org_name = party.find("./gmd:organizationName/gco:CharacterString", NS_MAP)

            if org_name is None:
                return None

            return self.lookup_organization(org_name.text.strip())
        else:
            raise ProcessingException(
                f"get_party_id called with invalid type of {party_type}"
            )

    def lookup_person(self, name, email):
        return super().lookup_person(name, email)

    def lookup_organization(self, name):
        return super().lookup_organization(name)

    def process(self):
        logger.debug(f"ISOProcessor.process '{self.identifier}'")

        dataset_subject = super().get_dataset_subject()

        # title -> schema:name
        for name in self.scimeta.findall(
            ".//gmd:identificationInfo/*/gmd:citation/gmd:CI_Citation/gmd:title/*",
            NS_MAP,
        ):
            self.model.append(
                RDF.Statement(
                    dataset_subject,
                    RDF.Node(RDF.Uri("https://schema.org/name")),
                    RDF.Node(name.text.strip()),
                )
            )

        # schema:description
        for description in self.scimeta.findall(
            ".//gmd:identificationInfo/*/gmd:abstract/*", NS_MAP
        ):
            self.model.append(
                RDF.Statement(
                    dataset_subject,
                    RDF.Node(RDF.Uri("https://schema.org/description")),
                    RDF.Node(element_text(description)),
                )
            )

        # schema:datePublished
        for citation_date in self.scimeta.findall(
            ".//gmd:identificationInfo/*/gmd:citation/gmd:CI_Citation/gmd:date/gmd:CI_Date",
            NS_MAP,
        ):
            # Skip if not a publication date
            date_type_code = citation_date.find(
                "./gmd:dateType/gmd:CI_DateTypeCode", NS_MAP
            )

            if date_type_code is None:
                continue

            date_type_code_value = date_type_code.text.strip()

            if date_type_code_value != "publication":
                continue

            self.model.append(
                RDF.Statement(
                    dataset_subject,
                    RDF.Node(RDF.Uri("https://schema.org/datePublished")),
                    RDF.Node(date_type_code_value),
                )
            )

        # dataset/creator -> schema:creator
        creators = self.process_creators()

        for creator in creators:
            self.model.append(
                RDF.Statement(
                    dataset_subject,
                    RDF.Node(RDF.Uri("https://schema.org/creator")),
                    creator,
                )
            )

        # gmd:descriptiveKeywords -> schema:keywords
        for keyword in self.scimeta.findall(
            ".//gmd:identificationInfo/*/gmd:descriptiveKeywords/gmd:MD_Keywords/gmd:keyword/*",
            NS_MAP,
        ):
            self.model.append(
                RDF.Statement(
                    dataset_subject,
                    RDF.Node(RDF.Uri("https://schema.org/keyword")),
                    RDF.Node(keyword.text.strip()),
                )
            )

        # dataset/project/funding -> schema:award
        # See eml220_processor.py for dataset/project/award processing
        for funding in self.scimeta.findall(".//dataset/project/funding", NS_MAP):
            self.model.append(
                RDF.Statement(
                    dataset_subject,
                    RDF.Node(RDF.Uri("https://schema.org/award")),
                    RDF.Node(element_text(funding)),
                )
            )

        # gmd:temporalElement -> schema:temporalCoverage
        self.process_temporal_coverage()

        # datset/coverage/spatialCoverage -> schema:spatialCoverage
        self.process_spatial_coverage()

        return super().process()

    def process_creators(self):
        creators = []

        # Add just owner, originator, author, principalInvestigator
        for party in self.scimeta.findall(
            ".//gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:citedResponsibleParty/gmd:CI_ResponsibleParty",
            NS_MAP,
        ):
            # Get an filter by role
            role = party.find("./gmd:role/gmd:CI_RoleCode", NS_MAP).text.strip()

            if role in ISO_CREATOR_ROLES:
                creators.append(party)

        return [self.process_party(creator) for creator in creators]

    def process_party(self, party):
        party_type = self.get_party_type(party)

        if party_type == "https://schema.org/Person":
            return self.process_person(party)
        elif party_type == "https://schema.org/Organization":
            return self.process_organization(party)
        else:
            logger.error(f"Getting the party type of {element_text(party)} failed")
            raise ProcessingException

    def process_person(self, party):
        person_id = self.get_party_id(party, PARTY_TYPE_PERSON)
        party_subject = RDF.Node(RDF.Uri(person_id))
        person_name = party.find("./gmd:individualName/gco:CharacterString", NS_MAP)

        # rdf:type
        self.model.append(
            RDF.Statement(
                party_subject,
                RDF.Node(RDF.Uri("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")),
                RDF.Node(RDF.Uri("https://schema.org/Person")),
            )
        )

        # schema:name
        self.model.append(
            RDF.Statement(
                party_subject,
                RDF.Node(RDF.Uri("https://schema.org/name")),
                person_name.text.strip(),
            )
        )

        # schema:affiliation
        for organization in party.findall(
            ".//gmd:organizationName/gco:CharacterString", NS_MAP
        ):
            affiliation_id = self.get_party_id(party, PARTY_TYPE_ORGANIZATION)
            organization_subject = RDF.Node(RDF.Uri(affiliation_id))

            # schema:affiliation
            self.model.append(
                RDF.Statement(
                    party_subject,
                    RDF.Node(RDF.Uri("https://schema.org/affiliation")),
                    organization_subject,
                )
            )

            # schema:Organization rdf:type
            self.model.append(
                RDF.Statement(
                    organization_subject,
                    RDF.Node(
                        RDF.Uri("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
                    ),
                    RDF.Node(RDF.Uri("https://schema.org/Organization")),
                )
            )

            # schema:Organization schema:name
            self.model.append(
                RDF.Statement(
                    organization_subject,
                    RDF.Node(RDF.Uri("https://schema.org/name")),
                    organization.text.strip(),
                )
            )

        # schema:email
        for email in party.findall(
            "./gmd:contactInfo/gmd:CI_Contact/gmd:address/gmd:CI_Address/gmd:electronicMailAddress/gco:CharacterString",
            NS_MAP,
        ):
            self.model.append(
                RDF.Statement(
                    party_subject,
                    RDF.Node(RDF.Uri("https://schema.org/email")),
                    email.text.strip(),
                )
            )

        return party_subject

    def process_organization(self, party):
        org_id = self.get_party_id(party, PARTY_TYPE_ORGANIZATION)
        party_subject = RDF.Node(RDF.Uri(org_id))
        org_name = party.find("./gmd:organizationName/gco:CharacterString", NS_MAP)

        # rdf:type
        self.model.append(
            RDF.Statement(
                party_subject,
                RDF.Node(RDF.Uri("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")),
                RDF.Node(RDF.Uri("https://schema.org/Organization")),
            )
        )

        # schema:name
        self.model.append(
            RDF.Statement(
                party_subject,
                RDF.Node(RDF.Uri("https://schema.org/name")),
                org_name.text.strip(),
            )
        )

        return party_subject

    def process_temporal_coverage(self):
        dataset_subject = self.get_dataset_subject()

        for time_instants in self.scimeta.findall(
            ".//gmd:identificationInfo/*/gmd:extent/gmd:EX_Extent/gmd:temporalElement/gmd:EX_TemporalExtent/gmd:extent/gml:TimeInstant/gml:timePosition",
            NS_MAP,
        ):
            self.model.append(
                RDF.Statement(
                    dataset_subject,
                    RDF.Node(RDF.Uri("https://schema.org/temporalCoverage")),
                    RDF.Node(time_instants.text.strip()),
                )
            )

        for time_period in self.scimeta.findall(
            ".//gmd:identificationInfo/*/gmd:extent/gmd:EX_Extent/gmd:temporalElement/gmd:EX_TemporalExtent/gmd:extent/gml:TimePeriod",
            NS_MAP,
        ):
            begin_position_text = time_period.find(
                "./gml:beginPosition", NS_MAP
            ).text.strip()
            end_position_text = time_period.find(
                "./gml:endPosition", NS_MAP
            ).text.strip()

            # Support intdeterminate end position using Schema.org/ISO ".." notation
            if len(end_position_text) == 0:
                end_position_text = ".."

            self.model.append(
                RDF.Statement(
                    dataset_subject,
                    RDF.Node(RDF.Uri("https://schema.org/temporalCoverage")),
                    RDF.Node(f"{begin_position_text}/{end_position_text}"),
                )
            )

    def process_spatial_coverage(self):
        dataset_subject = self.get_dataset_subject()

        for bounding_box in self.scimeta.findall(
            ".//gmd:identificationInfo/*/gmd:extent/gmd:EX_Extent/gmd:geographicElement/gmd:EX_GeographicBoundingBox",
            NS_MAP,
        ):
            # Set up blank nodes ahead of time
            place_bnode = RDF.Node(blank=str(uuid.uuid4()))
            geo_bnode = RDF.Node(blank=str(uuid.uuid4()))
            additional_property_wkt_bnode = RDF.Node(blank=str(uuid.uuid4()))
            additional_property_crs_bnode = RDF.Node(blank=str(uuid.uuid4()))

            # Get bounding box
            north = bounding_box.find(
                "gmd:northBoundLatitude/gco:Decimal", NS_MAP
            ).text.strip()
            east = bounding_box.find(
                "gmd:eastBoundLongitude/gco:Decimal", NS_MAP
            ).text.strip()
            south = bounding_box.find(
                "gmd:southBoundLatitude/gco:Decimal", NS_MAP
            ).text.strip()
            west = bounding_box.find(
                "gmd:westBoundLongitude/gco:Decimal", NS_MAP
            ).text.strip()

            # schema:spatialCoverage
            self.model.append(
                RDF.Statement(
                    dataset_subject,
                    RDF.Node(RDF.Uri("https://schema.org/spatialCoverage")),
                    place_bnode,
                )
            )

            # rdf:type
            self.model.append(
                RDF.Statement(
                    place_bnode,
                    RDF.Node(
                        RDF.Uri("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
                    ),
                    RDF.Node(RDF.Uri("https://schema.org/Place")),
                )
            )

            # Place -> schema:geo
            self.model.append(
                RDF.Statement(
                    place_bnode,
                    RDF.Node(RDF.Uri("https://schema.org/geo")),
                    geo_bnode,
                )
            )

            if north == south and east == west:
                # geo -> rdf:type
                self.model.append(
                    RDF.Statement(
                        geo_bnode,
                        RDF.Node(
                            RDF.Uri("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
                        ),
                        RDF.Node(RDF.Uri("https://schema.org/GeoCoordinates")),
                    )
                )

                # geo -> schema:latitude
                self.model.append(
                    RDF.Statement(
                        geo_bnode,
                        RDF.Node(RDF.Uri("https://schema.org/latitude")),
                        RDF.Node(f"{north}"),
                    )
                )

                # geo -> schema:longitude
                self.model.append(
                    RDF.Statement(
                        geo_bnode,
                        RDF.Node(RDF.Uri("https://schema.org/longitude")),
                        RDF.Node(f"{east}"),
                    )
                )

                # schema:additionalProperty
                self.model.append(
                    RDF.Statement(
                        place_bnode,
                        RDF.Node(RDF.Uri("https://schema.org/additionalProperty")),
                        additional_property_wkt_bnode,
                    )
                )

                # rdf:type
                self.model.append(
                    RDF.Statement(
                        additional_property_wkt_bnode,
                        RDF.Node(
                            RDF.Uri("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
                        ),
                        RDF.Node(RDF.Uri("https://schema.org/PropertyValue")),
                    )
                )

                # schema:propertyID
                self.model.append(
                    RDF.Statement(
                        additional_property_wkt_bnode,
                        RDF.Node(RDF.Uri("https://schema.org/propertyID")),
                        RDF.Node(RDF.Uri("http://www.wikidata.org/entity/Q4018860")),
                    )
                )

                # schema:value
                self.model.append(
                    RDF.Statement(
                        additional_property_wkt_bnode,
                        RDF.Node(RDF.Uri("https://schema.org/name")),
                        RDF.Node("Well-Known Text (WKT) representation of geometry"),
                    )
                )

                # schema:url
                self.model.append(
                    RDF.Statement(
                        additional_property_wkt_bnode,
                        RDF.Node(RDF.Uri("https://schema.org/value")),
                        RDF.Node(f"POINT ({west} {north})"),
                    )
                )
            else:
                # geo -> rdf:type
                self.model.append(
                    RDF.Statement(
                        geo_bnode,
                        RDF.Node(
                            RDF.Uri("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
                        ),
                        RDF.Node(RDF.Uri("https://schema.org/GeoShape")),
                    )
                )

                # geo -> schema:box
                self.model.append(
                    RDF.Statement(
                        geo_bnode,
                        RDF.Node(RDF.Uri("https://schema.org/box")),
                        RDF.Node(f"{north},{east} {south},{west}"),
                    )
                )

                # schema:additionalProperty
                self.model.append(
                    RDF.Statement(
                        place_bnode,
                        RDF.Node(RDF.Uri("https://schema.org/additionalProperty")),
                        additional_property_wkt_bnode,
                    )
                )

                # rdf:type
                self.model.append(
                    RDF.Statement(
                        additional_property_wkt_bnode,
                        RDF.Node(
                            RDF.Uri("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
                        ),
                        RDF.Node(RDF.Uri("https://schema.org/PropertyValue")),
                    )
                )

                # schema:propertyID
                self.model.append(
                    RDF.Statement(
                        additional_property_wkt_bnode,
                        RDF.Node(RDF.Uri("https://schema.org/propertyID")),
                        RDF.Node(RDF.Uri("http://www.wikidata.org/entity/Q4018860")),
                    )
                )

                # schema:value
                self.model.append(
                    RDF.Statement(
                        additional_property_wkt_bnode,
                        RDF.Node(RDF.Uri("https://schema.org/name")),
                        RDF.Node("Well-Known Text (WKT) representation of geometry"),
                    )
                )

                # schema:url
                self.model.append(
                    RDF.Statement(
                        additional_property_wkt_bnode,
                        RDF.Node(RDF.Uri("https://schema.org/value")),
                        RDF.Node(
                            f"POLYGON (({west} {north}, {east} {north}, {east} {south}, {west} {south}, {west} {north}))"
                        ),
                    )
                )

            # schema:additionalProperty
            self.model.append(
                RDF.Statement(
                    place_bnode,
                    RDF.Node(RDF.Uri("https://schema.org/additionalProperty")),
                    additional_property_crs_bnode,
                )
            )

            # rdf:type
            self.model.append(
                RDF.Statement(
                    additional_property_crs_bnode,
                    RDF.Node(
                        RDF.Uri("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
                    ),
                    RDF.Node(RDF.Uri("https://schema.org/PropertyValue")),
                )
            )

            # schema:propertyID
            self.model.append(
                RDF.Statement(
                    additional_property_crs_bnode,
                    RDF.Node(RDF.Uri("https://schema.org/propertyID")),
                    RDF.Node(RDF.Uri("http://www.wikidata.org/entity/Q4018860")),
                )
            )

            # schema:value
            self.model.append(
                RDF.Statement(
                    additional_property_crs_bnode,
                    RDF.Node(RDF.Uri("https://schema.org/name")),
                    RDF.Node("Spatial Reference System"),
                )
            )

            # schema:url
            self.model.append(
                RDF.Statement(
                    additional_property_crs_bnode,
                    RDF.Node(RDF.Uri("https://schema.org/value")),
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
        if party.find("./gmd:individualName", NS_MAP) is not None:
            return "https://schema.org/Person"
        elif party.find("./gmd:organizationName", NS_MAP) is not None:
            return "https://schema.org/Organization"
        else:
            return None
