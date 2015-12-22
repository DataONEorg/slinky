"""iso.py

Processing functions for extractingn person/organization information from
ISO metadata.

ISO (http://www.isotc211.org/2005/gmd) metadata allows the metadata author to
encode information on the metadata contact as well as the metadata contact.
For each type of contact, information about the contact person or organiation
is stored in a <gmd:CI_ResponsibleParty> element which contains sub-elements
used to store name, addresses, phone numbers, etc.

References:
- ftp://ftp.ncddc.noaa.gov/pub/Metadata/Online_ISO_Training/Transition_to_ISO/workbooks/MI_Metadata.pdf
- http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#CI_RoleCode"
"""

import re


def process(xmldoc, document):
    """Process the XML document for metadata and data contacts."""

    # Process metadata
    metadata_contacts = xmldoc.findall(".//gmd:contact/gmd:CI_ResponsibleParty")

    records = []

    for party in metadata_contacts:
        record = processResponsibleParty(party, document)
        record['source'] = 'contact'
        records.append(record)

    data_contacts = xmldoc.findall(".//gmd:contact/gmd:CI_ResponsibleParty")

    for party in metadata_contacts:
        record = processResponsibleParty(party, document)
        record['source'] = 'creator'
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

    # Creator a blank record with defaults
    record = { 'source': 'other' } # Default to non-creator role

    # individualName
    individ_name = party.find('./'+gmd+'individualName/'+gco+'CharacterString')

    if individ_name is not None:
        record['name'] = individ_name.text

    # organizationName
    org_name = party.find('./'+gmd+'organisationName/'+gco+'CharacterString')

    if org_name is not None:
        if record['type'] == 'person':
            record['organization'] = org_name.text
        elif record['type'] == 'organization':
            record['name'] = org_name.text

    # contactInfo
    contact_info = party.find('./'+gmd+'contactInfo/'+gmd+'CI_Contact')

    if contact_info is not None:


    # role
    role_code = party.find('./'+gmd+'role/CI_RoleCode')

    if role_code is not None:
        codeListValue = role_code.get('codeListValue')

        if codeListValue is not None and len(codeListValue) > 0:
            record['source'] = 'creator'


    records.append(record)

    return records


def processContactInfo(contact_info):
    """

      <gmd:contactInfo>
        <gmd:CI_Contact>
          <gmd:phone>
            <gmd:CI_Telephone>
              <gmd:voice>
                <gco:CharacterString>(775)682-5402</gco:CharacterString>
              </gmd:voice>
            </gmd:CI_Telephone>
          </gmd:phone>
          <gmd:address>
            <gmd:CI_Address>
              <gmd:deliveryPoint>
                <gco:CharacterString>University of nevada, Reno</gco:CharacterString>
              </gmd:deliveryPoint>
              <gmd:deliveryPoint>
                <gco:CharacterString>1664 N. Virginia St., MS 0171</gco:CharacterString>
              </gmd:deliveryPoint>
              <gmd:city>
                <gco:CharacterString>Reno</gco:CharacterString>
              </gmd:city>
              <gmd:administrativeArea>
                <gco:CharacterString>NV</gco:CharacterString>
              </gmd:administrativeArea>
              <gmd:postalCode>
                <gco:CharacterString>89557</gco:CharacterString>
              </gmd:postalCode>
              <gmd:country>
                <gco:CharacterString>USA</gco:CharacterString>
              </gmd:country>
              <gmd:electronicMailAddress>
                <gco:CharacterString>ericf@cse.unr.edu</gco:CharacterString>
              </gmd:electronicMailAddress>
            </gmd:CI_Address>
          </gmd:address>
          <gmd:onlineResource>
            <gmd:CI_OnlineResource>
              <gmd:linkage>
                <gmd:URL>http://sensor.nevada.edu</gmd:URL>
              </gmd:linkage>
              <gmd:name>
                <gco:CharacterString>provides information on the Nevada Climate Change Project and access to both the NevCAN (Nevada Climate-ecohydrology Assessment Network) and climate modeling output.</gco:CharacterString>
              </gmd:name>
            </gmd:CI_OnlineResource>
          </gmd:onlineResource>
        </gmd:CI_Contact>
      </gmd:contactInfo>
    """

    # Define prefixes
    gmd = '{http://www.isotc211.org/2005/gmd}'
    gco = '{http://www.isotc211.org/2005/gco}'
