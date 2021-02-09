"""iso.py

Processing functions for extractingn person/organization information from ISO
metadata.

ISO (http://www.isotc211.org/2005/gmd) metadata allows the metadata author to
encode information on the metadata contact as well as a 'cited responsible
party'. For each type of contact, information about the contact person or
organiation is stored in a <gmd:CI_ResponsibleParty> element which contains
sub-elements used to store name, addresses, phone numbers, etc.

The structure of the files is as follows (irrelevant parts omitted):

    <gmi:MI_Metadata>
        ...
        <gmd:contact>                               <---- metadata contact(s)
            <gmd:CI_ResponsibleParty>
        ...
        <gmd:identificationInfo>
            <gmd:MD_DataIdentification>             <---- data contact(s)
                <gmd:citation>
                    <gmd:citedResponsibleParty>
                        <gmd:CI_ResponsibleParty>
                    <gmd:citedResponsibleParty>
                        <gmd:CI_ResponsibleParty>
                    ...
        ...

Note: <gmd:citedResponsibleParty> elements can be found elsewhere (such as
inside aggregation information) and we want to ignore these too so our XPath
queries will need to be explicit.

The <contact> element is defined as:

    "The organisation directly responsible for the metadata maintenance. Contact
    information shall be provided."

The <citedResponsibleParty> element is defined as:

    "Identification of the contact for the resource"

Because the GeoLink concepts of contact and creator are at the Dataset level, we
only care about <citedResponsibleParty> elements and not <contact> elements.


References:

- ftp://ftp.ncddc.noaa.gov/pub/Metadata/Online_ISO_Training/Transition_to_ISO/workbooks/MI_Metadata.pdf
- http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#CI_RoleCode"
"""

import re


def process(xmldoc, document=None):
    """Process the XML document for metadata and data contacts."""

    gmd = '{http://www.isotc211.org/2005/gmd}'

    records = []

    # Process metadata
    parties = xmldoc.findall('.//'+gmd+'identificationInfo/'+gmd+'MD_DataIdentification/'+gmd+'citation/'+gmd+'CI_Citation/'+gmd+'citedResponsibleParty/'+gmd+'CI_ResponsibleParty')

    for party in parties:
        record = processResponsibleParty(party, document)

        # Returned record is None if it's invalid for some reason
        if record is not None:
            records.append(record)

    return records


def processResponsibleParty(party, document):
    """ Proccess a <processResponsibleParty> element.

    This element has five possible direct children;

    1. individualName
    2. organizationName
    3. positionName
    4. contactInfo
    5. role
    """

    # Define prefixes
    gmd = '{http://www.isotc211.org/2005/gmd}'
    gco = '{http://www.isotc211.org/2005/gco}'
    gmx = '{http://www.isotc211.org/2005/gmx}'

    # Set aside a blank record
    record = {}

    """individualName / organizationName

    The child element of these elements can be a gco:CharacterString or a
    gmx:Anchor
    """

    individ_name = party.find('./'+gmd+'individualName')
    org_name = party.find('./'+gmd+'organisationName')

    # Person
    if individ_name is not None:
        if len(individ_name) == 1:
            child_elem = individ_name[0]

            if child_elem is not None and child_elem.text is not None and len(child_elem.text) > 0:
                record['full_name'] = child_elem.text
                record['type'] = 'person'

        if org_name is not None:
            if len(org_name) == 1:
                child_elem = org_name[0]

                if child_elem is not None and child_elem.text is not None and len(child_elem.text) > 0:
                    record['organization'] = child_elem.text

    # Organization
    elif individ_name is None and org_name is not None:
        if len(org_name) == 1:
            child_elem = org_name[0]

            if child_elem is not None and child_elem.text is not None and len(child_elem.text) > 0:
                record['name'] = child_elem.text
                record['type'] = 'organization'

    # contactInfo
    contact = party.find('./'+gmd+'contactInfo/'+gmd+'CI_Contact')

    if contact is not None:
        contact_record = processCIContact(contact)

        for key in contact_record:
            if key in record:
                raise Exception("Key already found in record, failing to merge.")

            record[key] = contact_record[key]

    """role

    The ISO standard includes a pre-defined set of roles:

    resourceProvider:
        party that supplies the resource
    custodian:
        party that accepts accountability and responsibility for the data and ensures appropriate care and maintenance of the resource
    owner:
        party that owns the resource user party who uses the resource distributor party who distributes the resource
    originator:
        party who created the resource
    pointOfContact:
        party who can be contacted for acquiring knowledge about or acquisition of the resource
    principalInvestigator:
        key party responsible for gathering information and conducting research
    processor:
        party who has processed the data in a manner such that the resource has been modified
    publisher:
        party who published the resource
    author:
        party who authored the resource

    Here we map these values onto GeoLink concepts:

    pointOfContact -> isContactOf / hasContact
    originator -> isCreatorOf / hasCreator

    Other concepts are not mapped.
    """

    role_code = party.find('./'+gmd+'role/'+gmd+'CI_RoleCode')

    if role_code is not None:
        codeListValue = role_code.get('codeListValue')

        if codeListValue is not None and len(codeListValue) > 0:
            # http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml
            if codeListValue == 'originator':
                record['role'] = 'creator'
            elif codeListValue == 'pointOfContact':
                record['role'] = 'contact'

    # Reject invalid records instead of returning
    if 'type' not in record:
        return None

    if record['type'] == 'person':
        if 'full_name' not in record:
            return None

    elif record['type'] == 'organization':
        if 'name' not in record:
            return None

    if document is not None:
        record['document'] = document

    return record


def processCIContact(contact_info):
    """Extracts relevant fields from a gmd:CI_Contact element."""

    # Define prefixes
    gmd = '{http://www.isotc211.org/2005/gmd}'
    gco = '{http://www.isotc211.org/2005/gco}'

    # Store partial record
    record = {}

    # Address
    address = contact_info.find('./'+gmd+'address/'+gmd+'CI_Address')

    if address is not None:
        # Mailing address
        address_strings = [] # Just append each address part to a List

        delivery_points = address.findall('./'+gmd+'deliveryPoint/'+gco+'CharacterString')

        for dp in delivery_points:
            if dp.text is not None:
                address_strings.append(dp.text)

        city = address.find('./'+gmd+'city/'+gco+'CharacterString')

        if city is not None and city.text is not None:
            address_strings.append(city.text)

        admin_area = address.find('./'+gmd+'administrativeArea/'+gco+'CharacterString')

        if admin_area is not None and admin_area.text is not None:
            address_strings.append(admin_area.text)

        postal_code = address.find('./'+gmd+'postalCode/'+gco+'CharacterString')

        if postal_code is not None and postal_code.text is not None:
            address_strings.append(postal_code.text)

        country = address.find('./'+gmd+'country/'+gco+'CharacterString')

        if country is not None and country.text is not None:
            address_strings.append(country.text)

        if len(address_strings) > 0:
            record['address'] = " ".join(address_strings)

        # Email
        email = address.find('./'+gmd+'electronicMailAddress/'+gco+'CharacterString')

        if email is not None and email.text is not None:

            record['email'] = email.text
            print(record['email'])
            # Remove the email if it has spaces or zero length
            if len(record['email']) <= 0 or record['email'].find(' ') >= 0:
                record.pop('email', None)  # None is the return value

    # Phone
    phone = contact_info.find('./'+gmd+'phone/'+gmd+'CI_Telephone/'+gmd+'voice/'+gco+'CharacterString')

    if phone is not None and phone.text is not None:
        record['phone_number'] = phone.text

    return record
