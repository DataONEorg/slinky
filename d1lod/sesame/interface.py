import urllib
import uuid

from d1lod import dataone
from d1lod import validator
from d1lod import util

from d1lod.people import processing


class SesameInterface:
    def __init__(self, repository):
        self.repository = repository

    def __str__(self):
        print self.repository

    def count(self, subj_string, pred_string, obj_string):
        pass

    def exists(self, subj_string, pred_string, obj_string):
        pass

    def find(self, subj_string, pred_string, obj_string, literal=False):
        if literal == True:
            obj_string = "'%s'" % obj_string

        print "find(%s, %s, %s)" % (subj_string, pred_string, obj_string)

        return self.repository.find({'s': subj_string, 'p': pred_string, 'o': obj_string})

    def insert(self, subj_string, pred_string, obj_string, literal=False):

        if literal == True:
            obj_string = "'%s'" % obj_string
        print "insert(%s, %s, %s)" % (subj_string, pred_string, obj_string)

        self.repository.insert({'s': subj_string, 'p': pred_string, 'o': obj_string})

    def delete(self, subj_string, pred_string, obj_string, literal=False):
        if literal == True:
            obj_string = "'%s'" % obj_string
        print "delete(%s, %s, %s)" % (subj_string, pred_string, obj_string)

        self.repository.delete({'s': subj_string, 'p': pred_string, 'o': obj_string})

    def datasetExists(self, identifier):
        identifier_esc = urllib.quote_plus(identifier)

        result = self.find('d1dataset:'+identifier_esc, '?p', '?o')

        if result is None or len(result) <= 0:
            return False
        else:
            return True

    def addDataset(self, doc):
        identifier = dataone.extractDocumentIdentifier(doc)
        identifier_esc = urllib.quote_plus(identifier)

        # Delete if dataset is already in graph
        if self.datasetExists(identifier):
            self.deleteDataset(identifier)

        scimeta = dataone.getScientificMetadata(identifier, cache=True)
        records = processing.extractCreators(identifier, scimeta)

        vld = validator.Validator()
        formats = util.loadFormatsMap()

        # Add people and organizations
        people = [p for p in records if 'type' in p and p['type'] == 'person']
        organizations = [o for o in records if 'type' in o and o['type'] == 'organization']

        # Always do organizations first, so peoples' organization URIs exist
        for organization in organizations:
            organization = vld.validate(organization)
            self.addOrganization(organization)

        for person in people:
            person = vld.validate(person)
            self.addPerson(person)

        self.addDatasetTriples(doc, formats)

    def addDatasetTriples(self, doc, formats):
        identifier = dataone.extractDocumentIdentifier(doc)
        identifier_esc = urllib.quote_plus(identifier)
        dataset_uri_string = 'd1dataset:'+identifier_esc

        # type Dataset
        self.insert(dataset_uri_string, 'rdf:type', 'glbase:Dataset')

        # Title
        title_element = doc.find("./str[@name='title']")

        if title_element is not None:
            self.insert(dataset_uri_string, 'rdfs:label', title_element.text, literal=True)

        # Add glbase Identifier
        self.addIdentifierTriples(identifier)

        # Abstract
        abstract_element = doc.find("./str[@name='abstract']")

        if (abstract_element is not None):
            self.insert(dataset_uri_string, 'glbase:description', abstract_element.text, literal=True)

        # Spatial Coverage
        bound_north = doc.find("./float[@name='northBoundCoord']")
        bound_east = doc.find("./float[@name='eastBoundCoord']")
        bound_south = doc.find("./float[@name='southBoundCoord']")
        bound_west = doc.find("./float[@name='westBoundCoord']")

        if all(ele is not None for ele in [bound_north, bound_east, bound_south, bound_west]):
            if bound_north.text == bound_south.text and bound_west.text == bound_east.text:
                wktliteral = "POINT (%s %s)" % (bound_north.text, bound_east.text)
            else:
                wktliteral = "POLYGON ((%s %s, %s %s, %s %s, %s, %s))" % (bound_west.text, bound_north.text, bound_east.text, bound_north.text, bound_east.text, bound_south.text, bound_west.text, bound_south.text)

            self.insert(dataset_uri_string, 'glbase:hasGeometryAsWktLiteral', wktliteral, literal=True)

        # Temporal Coverage
        start_date = doc.find("./date[@name='startDate']")
        end_date = doc.find("./date[@name='endDate']")

        if start_date is not None:
            self.insert(dataset_uri_string, 'glbase:hasStartDate', start_date.text, literal=True)

        if end_date is not None:
            self.insert(dataset_uri_string, 'glbase:hasEndDate', end_date.text, literal=True)

        # Repositories: authoritative, replica, origin
        # Authoritative MN
        repository_authMN = doc.find("./str[@name='authoritativeMN']")

        if repository_authMN is not None:
            self.insert(dataset_uri_string, 'glbase:hasAuthoritativeDigitalRepository', 'd1repo:'+repository_authMN.text)

        # Replica MN's
        repository_replicas = doc.findall("./arr[@name='replicaMN']/str")

        for repo in repository_replicas:
            self.insert(dataset_uri_string, 'glbase:hasReplicaDigitalRepository', 'd1repo:'+repository_authMN.text)

        # Origin MN
        repository_datasource = doc.find("./str[@name='datasource']")

        if repository_datasource is not None:
            self.insert(dataset_uri_string, 'glbase:hasOriginDigitalRepository', 'd1repo:'+repository_datasource.text)

        # Obsoletes as PROV#wasRevisionOf
        obsoletes_node = doc.find("./str[@name='obsoletes']")

        if obsoletes_node is not None:
            other_document = urllib.quote_plus(obsoletes_node.text)
            self.insert(dataset_uri_string, 'prov:wasRevisionOf', 'd1dataset:'+other_document)

        # Landing page
        self.insert(dataset_uri_string, 'glbase:hasLandingPage', 'd1landing:'+identifier_esc)

        # Digital Objects
        # If this document has a resource map, get digital objects from there
        # Otherwise, use the cito:documents field in Solr

        resource_map_identifiers = doc.findall("./arr[@name='resourceMap']/str")

        if resource_map_identifiers is not None:
            for resource_map_node in resource_map_identifiers:
                resource_map_identifier = resource_map_node.text
                digital_objects = dataone.getAggregatedIdentifiers(resource_map_identifier)

                for digital_object in digital_objects:
                    self.addDigitalObject(identifier, urllib.unquote(digital_object), formats)
        else:
            digital_objects = doc.findall("./arr[@name='documents']/str")

            for digital_object in digital_objects:
                data_id = digital_object.text
                data_id_esc = urllib.quote_plus(data_id)

                self.addDigitalObject(identifier, data_id_esc, formats)

    def deleteDataset(self, identifier):
        self.deleteDatasetTriples(identifier)

    def deleteDatasetTriples(self, identifier):
        """ TODO
        Delete:
            All dataset ?p ?o triples
            All digital objects
            People that are creator of
            Organizations that are creator of
        """

        identifier_esc = urllib.quote_plus(identifier)

        self.delete('d1dataset:'+identifier_esc, '?p', '?o')
        self.delete('?s', 'glbase:isCreatorOf', '?o')

        parts_of = self.find('?s', 'glbase:isPartOf', 'd1dataset:'+identifier_esc)
        print parts_of
        digital_object_uris = set()

        for part in parts_of:
            digital_object_uris.add(part['s'])

        for digital_object_uri in digital_object_uris:
            self.delete(digital_object_uri, '?p', '?o')

    def addDigitalObject(self, dataset_identifier, digital_object_identifier, formats):
        # TODO: Delete the digital object's triples if it already exists, then add

        self.addDigitalObjectTriples(dataset_identifier, digital_object_identifier, formats)

    def addDigitalObjectTriples(self, dataset_identifier, digital_object_identifier, formats):
        dataset_identifier_esc = urllib.quote_plus(dataset_identifier)
        digital_object_identifier_esc = urllib.quote_plus(digital_object_identifier)

        """ Deal with the common case where a dataset PID is the same PID as its
        metadata record. In this case, just append '#metadata' to the URI. If
        we don't do this, the dataset PID will be typed as a Dataset _and_ and
        a DigitalObject."""

        # TODO: Check whether this is a good idea
        if dataset_identifier_esc == digital_object_identifier_esc:
            digital_object_identifier_esc = digital_object_identifier_esc + '#metadata'

        self.insert('d1dataset:'+digital_object_identifier_esc, 'rdf:type', 'glbase:DigitalObject')
        self.insert('d1dataset:'+digital_object_identifier_esc, 'glbase:isPartOf', 'd1dataset:'+dataset_identifier_esc)

        self.addIdentifierTriples(digital_object_identifier)

        # Get data object meta
        data_meta = dataone.getSystemMetadata(digital_object_identifier_esc, cache=True)

        if data_meta is None:
            print "Metadata for data object %s was not found. Continuing to next data object." % digital_object_identifier
            return

        # Checksum and checksum algorithm
        checksum_node = data_meta.find(".//checksum")

        if checksum_node is not None:
            self.insert('d1dataset:'+digital_object_identifier_esc, 'glbase:hasChecksum', checksum_node.text, literal=True)
            self.insert('d1dataset:'+digital_object_identifier_esc, 'glbase:hasChecksumAlgorithm', checksum_node.get("algorithm"), literal=True)

        # Size
        size_node = data_meta.find("./size")

        if size_node is not None:
            self.insert('d1dataset:'+digital_object_identifier_esc, 'glbase:hasByteLength', size_node.text, literal=True)

        # Format
        format_id_node = data_meta.find("./formatId")

        if format_id_node is not None:
            if format_id_node.text in formats:
                self.insert('d1dataset:'+digital_object_identifier_esc, 'glbase:hasFormat', formats[format_id_node.text]['uri'])

            else:
                print "Format not found."

        # Date uploaded
        date_uploaded_node = data_meta.find("./dateUploaded")

        if date_uploaded_node is not None:
            self.insert('d1dataset:'+digital_object_identifier_esc, 'glbase:dateUploaded', date_uploaded_node.text, literal=True)

        # Submitter and rights holders
        # submitter_node = data_meta.find("./submitter")
        #
        # if submitter_node is not None:
        #     submitter_node_text = " ".join(re.findall(r"o=(\w+)", submitter_node.text, re.IGNORECASE))
        #
        #     if len(submitter_node_text) > 0:
        #         self.insert('d1dataset:'+data_id, 'glbase:hasCreator', ])


        # rights_holder_node = data_meta.find("./rightsHolder")
        #
        # if rights_holder_node is not None:
        #     rights_holder_node_text = " ".join(re.findall(r"o=(\w+)", rights_holder_node.text, re.IGNORECASE))
        #
        #     if len(rights_holder_node_text) > 0:
        #         addStatement(model, d1dataset+data_id, ns["glbase"]+"hasRightsHolder", RDF.Uri("urn:node:" + rights_holder_node_text.upper()))

    def addPerson(self, record):
        if record is None:
            return

        person_uri = self.findPersonURI(record)

        if person_uri is None:
            person_uri = self.mintPersonURI()

        self.addPersonTriples(person_uri, record)

    def addPersonTriples(self, uri, record):
        self.insert(uri, 'rdf:type', 'glbase:Person')

        if 'salutation' in record:
            self.insert(uri, 'glbase:namePrefix', record['salutation'], literal=True)

        if 'full_name' in record:
            self.insert(uri, 'glbase:nameFull', record['full_name'], literal=True)

        if 'first_name' in record:
            self.insert(uri, 'glbase:nameGiven', record['first_name'], literal=True)

        if 'last_name' in record:
            self.insert(uri, 'glbase:nameFamily', record['last_name'], literal=True)

        if 'organization' in record:
            if self.organizationExists(record['organization']):
                organization_uri = self.findOrganization({'name':record['organization']})
            else:
                organization_uri = self.mintURI('d1org')
                self.insert(organization_uri, 'rdfs:label', record['organization'], literal=True)

            self.insert(uri, 'glbase:hasAffiliation', organization_uri)

        if 'email' in record:
            self.insert(uri, 'foaf:mbox', '<mailto:'+record['email']+'>')

        if 'address' in record:
            self.insert(uri, 'glbase:address', record['address'], literal=True)

        if 'document' in record:
            self.insert(uri, 'glbase:isCreatorOf', 'd1dataset:' + urllib.quote_plus(record['document']))

    def addOrganization(self, record):
        if record is None:
            return

        organization_uri = self.findOrganizationURI(record)

        if organization_uri is None:
            organization_uri = self.mintOrganizationURI()

        self.addOrganizationTriples(organization_uri, record)

    def addOrganizationTriples(self, uri, record):
        self.insert(uri, 'rdf:type', 'glbase:Organization')

        if 'name' in record:
            self.insert(uri, 'rdfs:label', record['name'], literal=True)

        if 'email' in record:
            self.insert(uri, 'foaf:mbox', '<mailto:'+record['email']+'>')

        if 'address' in record:
            self.insert(uri, 'glbase:address', record['address'], literal=True)

        if 'document' in record:
            self.insert(uri, 'glbase:isCreatorOf', 'd1dataset:' + record['document'])

    def findPersonURI(self, record):
        if record is None:
            return None

        if 'last_name' in record and 'email' in record:
            last_name = record['last_name']
            email = record['email']

            query_string = """
            SELECT ?s
            WHERE {
                ?s rdf:type glbase:Person .
                ?s glbase:nameFamily '%s' .
                ?s foaf:mbox <mailto:%s>

            }
            """ % (last_name, email)

            find_result = self.repository.query(query_string)

            if find_result is None or len(find_result) <= 0:
                return None

            # Temporary approach to choosing the best URI
            return find_result[0]['s']

        return None

    def findOrganizationURI(self, record):
        if record is None:
            return None

        if 'name' in record:
            name = record['name']

            query_string = """
            SELECT ?s
            WHERE {
                ?s rdf:type glbase:Organization .
                ?s rdfs:label '%s'
            }
            """ % name

            find_result = self.repository.query(query_string)

            if find_result is None or len(find_result) <= 0:
                return None

            # Temporary approach to choosing the best URI
            return find_result[0]['s']

        return None

    def mintPersonURI(self):
        new_uuid = str(uuid.uuid4())
        uri_string = "d1person:urn:uuid:%s" % new_uuid

        return uri_string

    def mintOrganizationURI(self):
        new_uuid = str(uuid.uuid4())
        uri_string = "d1org:urn:uuid:%s" % new_uuid

        return uri_string

    def addIdentifierTriples(self, identifier):
        identifier_esc = urllib.quote_plus(identifier)
        identifier_uri = "d1dataset:%s#identifier>" % identifier_esc
        identifier_scheme = self.getIdentifierScheme(identifier)

        self.insert(identifier_uri, 'rdf:type', 'glbase:Identifier')
        self.insert(identifier_uri, 'glbase:hasIdentifierValue', identifier_esc, literal=True)
        self.insert(identifier_uri, 'rdfs:label', identifier_esc, literal=True)
        self.insert(identifier_uri, 'glbase:hasIdentifierScheme', 'datacite:'+identifier_scheme)
        self.insert('d1dataset:'+identifier_esc, 'glbase:hasIdentifier', identifier_uri)

    def getIdentifierScheme(self, identifier):
        if (identifier.startswith("doi:") |
                identifier.startswith("http://doi.org/") | identifier.startswith("https://doi.org/") |
                identifier.startswith("https://dx.doi.org/") | identifier.startswith("https://dx.doi.org/")):
            scheme = 'doi'
        elif (identifier.startswith("ark:")):
            scheme = 'ark'
        elif (identifier.startswith("http:")):
            scheme = 'uri'
        elif (identifier.startswith("https:")):
            scheme = 'uri'
        elif (identifier.startswith("urn:")):
            scheme = 'urn'
        else:
            scheme = 'local-resource-identifier-scheme'

        return scheme
