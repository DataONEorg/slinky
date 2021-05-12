import re

DOI_PATTERN = re.compile(r"(10\.\d{4,9}\/[-._;()\/:A-Z0-9]+)", re.IGNORECASE)
ORCID_PATTERN = re.compile(r"(\d{4}-\d{4}-\d{4}-[\dX]{4})", re.IGNORECASE)

PARTY_TYPE_PERSON = "person"
PARTY_TYPE_ORGANIZATION = "organization"


def element_text(element):
    return " ".join([item for item in element.itertext()]).strip()


def is_doi(identifier):
    return DOI_PATTERN.search(identifier) != None


def get_doi(identifier):
    result = DOI_PATTERN.search(identifier)

    if result is None:
        return None

    return result.group(1)


def is_orcid(text):
    return ORCID_PATTERN.search(text) != None


def get_orcid(text):
    result = ORCID_PATTERN.search(text)

    if result is None:
        return None

    return result.group(1)
