"""test_metadata.py

Tests for the metadata processing routines.
"""

import StringIO
import xml.etree.ElementTree as ET

from d1lod.metadata import *


def test_iso_ignores_metadata_contacts():
    """Test that the processer ignores responsible parties that are contacts
    and not citedResponsibleParties."""

    doc = ET.parse('tests/data/metadata/iso/contact.xml')
    assert iso.process(doc) == []


def test_iso_ignores_empty_elements():
    """Test that the processer doesn't break when elements are empty."""

    doc = ET.parse('tests/data/metadata/iso/emptystrings.xml')
    assert iso.process(doc) == []


def test_can_process_a_simple_file():
    doc = ET.parse('tests/data/metadata/iso/creator.xml')
    assert iso.process(doc) == [
        {
            'address': 'delivery point line 1 delivery point line 2 city state zip country',
            'email': 'example@example.org',
            'name': 'org_name',
            'phone_number': '(555) 555-5555',
            'type': 'organization',
            'role': 'creator'
        }
    ]


def test_can_include_document_pid():
    """Test that the processer attaches the document PID to the record."""

    doc = ET.parse('tests/data/metadata/iso/creator.xml')
    records = iso.process(doc, 'xxx')

    assert len(records) == 1
    assert 'document' in records[0]
    assert records[0]['document'] == 'xxx'


def test_iso_can_process_a_file_with_a_creator():
    """Test that the processer can extract a creator record from a document with
    a citedResponsibleParty"""

    doc = ET.parse('tests/data/metadata/iso/creator.xml')

    records = iso.process(doc)

    assert len(records) == 1
    print records
    assert 'role' in records[0]
    assert records[0]['role'] == 'creator'


def test_iso_can_process_a_ncei_file():
    """Regression test for processing an NCEI ISO metadata file.

    URL:
        http://data.nodc.noaa.gov/geoportal/csw?getxml=%7B0EDDBAC4-C740-45C4-9442-18FEC1227FAD%7D
    """

    doc = ET.parse('tests/data/metadata/iso/ncei.xml')
    records = iso.process(doc)
    creators = [record for record in records if 'role' in record and record['role']=='creator']
    assert len(records) == 5
    assert len(creators) == 1
