"""
d1lod.interface

A high-level wrapper around a d1lod.graph that implements a variety
of d1lod-specific methods.

The most common method that will be called by will be addDataset(). This method
takes care of the work of adding the dataset, its digital objects, and its
people and organizations to the graph. All statements for a dataset are
accumulated into a temporary Redland's RDF.Model w/ an in-memory storage. When
all the triples for a dataset are accumulated, those triples are converted into
a SPARQL UPDATE query string and passed to the Graph to be inserted into
the graph database.

Aside from the basic methods (count, exists, etc), a general pattern is followed
for method naming of having separate methods such as addDataset and
addDatasetTriples (note the addition of the 'Triples' to the name). This pattern
is used to separate concerns, where the former is concerned with higher-level
issue such as whether or not a dataset should be added in the first place and
the latter is concerned with adding the triples for that dataset to the graph.

http://docs.s4.ontotext.com/display/S4docs/Fully+Managed+Database#FullyManagedDatabase-cURL%28dataupload%29
"""

import urllib
import uuid
import re
import RDF
import logging

import dataone, validator, util
from d1lod.people import processing

# Default namespaces
NAMESPACES = {
    'owl': 'http://www.w3.org/2002/07/owl#',
    'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
    'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    'xsd': 'http://www.w3.org/2001/XMLSchema#',
    'foaf': 'http://xmlns.com/foaf/0.1/',
    'dcterms': 'http://purl.org/dc/terms/',
    'datacite': 'http://purl.org/spar/datacite/',
    'prov': 'http://www.w3.org/ns/prov#',
    'geolink': 'http://schema.geolink.org/1.0/base/main#',
    'd1dataset': 'http://lod.dataone.org/dataset/',
    'd1person': 'http://lod.dataone.org/person/',
    'd1org': 'http://lod.dataone.org/organization/',
    'd1node': 'https://cn.dataone.org/cn/v1/node/'
}


class Interface:
    def __init__(self, graph):
        """Initialize a graph with the given name.

        Parameters:
        -----------

        graph : str
            The name of the graph.
        """

        self.graph = graph

        # Load the formats map
        self.formats = util.loadFormatsMap()

        # Set up the temporary model which accumulates triples when addDataset
        # is called
        self.model = None

        # Synchronize the newly added namespaces to the Graph object
        # for faster referencing
        self.graph.ns = NAMESPACES

        # Add fixed statements
        #
        # Note: These are inserted regardless of whether or not they already
        # exist

        prov = self.graph.ns['prov']
        owl = self.graph.ns['owl']

        self.graph.insert(RDF.Uri(prov+'wasRevisionOf'), RDF.Uri(owl+'inverseOf'), RDF.Uri(prov+'hadRevision'))


    def __str__(self):
        return "Interface to Graph: '%s'." % self.graph.name


    def prepareTerm(self, term):
        """Prepare an RDF term to be added to an RDF Model.

        A term is either:
            - An RDF.Node
            - An RDF.Uri
            - A string, which is either:
                - A binding string (e.g., '?s')
                - A URI reference (e.g., 'rdf:type')
                - A URI (e.g., http://...)
                - A literal

        If the term is a str with a namespace prefix that the Interface knows
        about then that namespace will be interpolated prior to making the term
        into an RDF.Uri.

        Arguments:

            term :  str | RDF.Node | RDF.Uri
                The RDF term (subject, predicate, or object) to be prepared.

        Returns:
            str | RDF.Node | RDF.Uri
        """

        if isinstance(term, RDF.Uri) or isinstance(term, RDF.Node):
            return term
        elif isinstance(term, str) or isinstance(term, unicode):
            # Binding?: Do nothing
            if term.startswith('?'):
                return term

            # Conver 'http...' strings to RDF.Uri
            if term.startswith('http'):
                return RDF.Uri(term)

            parts = term.split(':')
            # URI
            if len(parts) > 1 and parts[0] in self.graph.ns:
                prefix = self.graph.ns[parts[0]]
                other_parts = parts[1:]

                term = RDF.Uri(prefix + ':'.join(other_parts))
            else:
                # Literal
                term = RDF.Node(term)
        else:
            raise Exception("Invalid term sent can't be prepared: (type is %s) Term is `%s`." % (type(term), term))

        return term


    def createModel(self):
        """Creates a Redland RDF Model.

        Returns:
            RDF.Model
        """

        storage = RDF.HashStorage("temp", options="new='yes',hash-type='memory'")

        if storage is None:
            raise Exception("new RDF.Storage failed")

        model = RDF.Model(storage)

        if model is None:
            raise Exception("new RDF.model failed")

        self.model = model


    def insertModel(self):
        """Inserts the current RDF Model (if it exists) into the graph and
        deletes it if successful."""

        if self.model is None:
            print "Attempted to insert a model that was None."
            return

        # checking for all the statements in the current model
        # if either subject / object / predicate is a blank node - then indicate that the payload contains a blank node
        blank_node = False
        for s in self.model:
            blank_node = self.tripleHasBlankNode(s.subject, s.predicate, s.object)
            if(blank_node == True):
                break

        sparql_data = " .\n ".join([str(s) for s in self.model])

        # Log model size
        logging.info('Inserting model of size %d.', self.model.size())

        self.graph.insert_data(payload=sparql_data, blank_node=blank_node)


    def add(self, s, p, o):
        """Adds a triple to the current model.

        Performs pre-processing on the subject, predicate, and objects
        convert each one into an RDF.Node or RDF.Uri if it isn't already.
        Pre-processing will perform namespace interpolation, e.g. if
        s=='foo:Bar' and the namespace 'foo' exists and is http://foo.com/, the pre-processing step will convert s to
        RDF.Uri('<http://foo.com/Bar').


        Parameters:
        -----------

        s : RDF.Node | str
            The subject of the triple pattern.

        p : RDF.Node | str
            The predicate of the triple pattern.

        o : RDF.Node | str
            The object of the triple pattern.

        Examples:
        ---------

            add(RDF.Uri('http://example.com/#me'), 'rdfs:label', 'Myself')
            add(RDF.Uri('http://example.com/#me'), 'rdfs:label', RDF.Node('Myself'))
            add(RDF.Uri('http://example.com/#me'), 'rdfs:label', RDF.Node('Myself'))
        """

        if self.model is None:
            print "Failed to add triple to model because there was no current model."
            return

        # - Converts strings to Nodes or Uris, whichever is appropriate
        s = self.prepareTerm(s)
        p = self.prepareTerm(p)
        o = self.prepareTerm(o)
        st = ""

        try:
            st = RDF.Statement(s, p, o)
        except:
            print "Failed to create statement."

        try:
            self.model.append(st)
        except RDF.RedlandError:
            print "Failed to add statement: %s" % st


    def exists(self, s='?s', p='?p', o='?o'):
        """Determine whether any triples matching the given pattern exist in
        the graph.

        Parameters:
        -----------

        s : str
            The subject of the triple pattern.

        p : str
            The predicate of the triple pattern.

        o : str
            The object of the triple pattern.

        Returns:
        --------

        bool
            Whether or not any triples with the pattern exist in the Graph.
        """

        result = self.find(s=s, p=p, o=o, limit=1)

        if result is None:
            return False

        if len(result) > 0 and 'error-message' in result[0]:
            print result[0]['error-message']
            return False

        if len(result) > 0:
            return True

        return False


    def find(self, s='?s', p='?p', o='?o', limit=100):
        """Finds triples in the graph matching the given pattern.

        Parameters:
        -----------

        s : RDF.Node | str
            The subject of the triple pattern.

        p : RDF.Node | str
            The predicate of the triple pattern.

        o : RDF.Node | str
            The object of the triple pattern.

        Returns:
        --------

        List
            A list of Dicts with names s, p, and o.
        """

        s = self.prepareTerm(s)
        p = self.prepareTerm(p)
        o = self.prepareTerm(o)

        # checks if the payload contains a blank node or not
        blank_node = self.tripleHasBlankNode(s, p, o)

        if isinstance(s, RDF.Uri):
            s = '<' + str(s) + '>'

        if isinstance(p, RDF.Uri):
            p = '<' + str(p) + '>'

        if isinstance(o, RDF.Uri):
            o = '<' + str(o) + '>'

        query = u"""
        SELECT * WHERE { %s %s %s } LIMIT %d
        """ % (s, p, o, limit)

        return self.graph.query(query, blank_node=blank_node)


    def delete(self, s='?s', p='?p', o='?o'):
        """Delete all triples matching the given pattern from the graph.

        Parameters:
        -----------

        s : str
            The subject of the triple pattern.

        p : str
            The predicate of the triple pattern.

        o : str
            The object of the triple pattern.
        """

        s = self.prepareTerm(s)
        p = self.prepareTerm(p)
        o = self.prepareTerm(o)



        # checks if the payload contains a blank node or not
        blank_node = self.tripleHasBlankNode(s, p, o)

        if isinstance(s, RDF.Uri):
            s = '<' + str(s) + '>'

        if isinstance(p, RDF.Uri):
            p = '<' + str(p) + '>'

        if isinstance(o, RDF.Uri):
            o = '<' + str(o) + '>'

        payload_data = u"%s %s %s" % (s, p, o)

        return self.graph.delete_data(payload=payload_data, blank_node=blank_node)


    def datasetExists(self, identifier):
        """Determines whether a dataset exists in the graph.

        The criterion used for existence is whether or not *any* triples with
        the given identifier exist in the graph.

        Parameters:
        -----------

        identifier : str
            Non-urlencoded DataOne identifier

        Returns:
        --------

        bool
            Whether or not the dataset exists.
        """

        identifier_esc = urllib.unquote(identifier).decode('utf8')

        result = self.find(s='d1dataset:'+identifier_esc, limit=1)

        if result is None or len(result) <= 0:
            return False
        else:
            return True


    def addDataset(self, identifier, doc=None):
        """Adds a dataset to the graph.

        Parameters:
        -----------
        identifier : str
            Non-urlencoded DataOne identifier

        doc : XML Element
            An XML element containing a result from the Solr index which
            contains a number of fields relating to a dataset.

        """

        if self.model is not None:
            raise Exception("Model existed when addDataset was called. This means the last Model wasn't cleaned up after finishing.")

        self.createModel()

        # Get Solr fields if they weren't passed in
        if doc is None:
            doc = dataone.getSolrIndexFields(identifier)

        identifier = dataone.extractDocumentIdentifier(doc)
        identifier_esc = urllib.unquote(identifier).decode('utf8')

        dataset_node = RDF.Uri(self.graph.ns['d1dataset'] + identifier_esc)

        self.add(dataset_node, 'rdf:type', 'geolink:Dataset')

        # Delete if dataset is already in graph
        if self.datasetExists(identifier):
            logging.info("Dataset with identifier %s already exists. Deleting then re-adding.", identifier)
            self.deleteDataset(identifier)

        scimeta = dataone.getScientificMetadata(identifier)
        records = processing.extractCreators(identifier, scimeta)

        vld = validator.Validator()

        # Add Dataset triples first, we'll use them when we add people
        # to match to existing people by the current dataset's 'obsoletes' field

        self.addDatasetTriples(dataset_node, doc)

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

        # Commit or reject the model here
        if self.model is None:
            raise Exception("Model was None. It should have been an RDF.Model.")

        self.insertModel()
        self.model = None  # Remove the model since we're done


    def addDatasetTriples(self, dataset_node, doc):
        if self.model is None:
            raise Exception("Model not found.")

        identifier = dataone.extractDocumentIdentifier(doc)
        identifier_esc = urllib.unquote(identifier).decode('utf8')

        # type Dataset
        self.add(dataset_node, 'rdf:type', 'geolink:Dataset')

        # Title
        title_element = doc.find("./str[@name='title']")

        if title_element is not None:
            self.add(dataset_node, 'rdfs:label', RDF.Node(title_element.text))

        # Add geolink:Identifier
        self.addIdentifierTriples(dataset_node, identifier)

        # Abstract
        abstract_element = doc.find("./str[@name='abstract']")

        if (abstract_element is not None):
            self.add(dataset_node, 'geolink:description', RDF.Node(abstract_element.text))

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

            self.add(dataset_node, 'geolink:hasGeometryAsWktLiteral', RDF.Node(wktliteral))

        # Temporal Coverage
        begin_date = doc.find("./date[@name='beginDate']")
        end_date = doc.find("./date[@name='endDate']")

        if begin_date is not None:
            self.add(dataset_node, 'geolink:hasStartDate', RDF.Node(begin_date.text))

        if end_date is not None:
            self.add(dataset_node, 'geolink:hasEndDate', RDF.Node(end_date.text))

        # Obsoletes as PROV#wasRevisionOf
        obsoletes_node = doc.find("./str[@name='obsoletes']")

        if obsoletes_node is not None:
            other_document_esc = urllib.unquote(obsoletes_node.text).decode('utf8')
            self.add(dataset_node, 'prov:wasRevisionOf', RDF.Uri(self.graph.ns['d1dataset'] + other_document_esc))

        # Landing page
        self.add(dataset_node, 'geolink:hasLandingPage', RDF.Uri("https://search.dataone.org/#view/" + identifier_esc))


        # Digital Objects
        # If this document has a resource map, get digital objects from there
        # Otherwise, use the cito:documents field in Solr

        resource_map_identifiers = doc.findall("./arr[@name='resourceMap']/str")

        if len(resource_map_identifiers) > 0:
            for resource_map_node in resource_map_identifiers:
                resource_map_identifier = resource_map_node.text

                digital_objects = dataone.getAggregatedIdentifiers(resource_map_identifier)

                for digital_object in digital_objects:
                    digital_object_identifier = urllib.unquote(digital_object).decode('utf8')
                    self.addDigitalObject(identifier, digital_object_identifier)
        else:
            # If no resourceMap or documents field, at least add the metadata
            # file as a digital object
            # dataUrl e.g. https://cn.dataone.org/cn/v1/resolve/doi%3A10.6073%2FAA%2Fknb-lter-cdr.70061.123

            data_url_node = doc.find("./str[@name='dataUrl']")

            if data_url_node is not None:
                data_url = data_url_node.text
                digital_object = dataone.extractIdentifierFromFullURL(data_url)
                digital_object = urllib.unquote(digital_object).decode('utf8')

                self.addDigitalObject(identifier, digital_object)


    def deleteDataset(self, identifier):
        self.deleteDatasetTriples(identifier)


    def deleteDatasetTriples(self, identifier):
        """Delete all triples about this dataset. This includes:

        - The dataset triples themselves (title, start date, etc)
        - The dataset's digital objects
        - The identifiers for the dataset and digital object(s)
        - The isCreatorOf statement for people and organizations

        This is a bit of extra work because identifiers and digital objects
        are blank nodes and querying those takes some multi-statement SPARQL
        queries.
        """

        # Prepare some SPARQL query terms
        identifier_esc = urllib.unquote(identifier).decode('utf8')
        dataset = RDF.Uri(self.graph.ns['d1dataset']+identifier_esc)
        has_identifier = RDF.Uri(self.graph.ns['geolink']+'hasIdentifier')
        is_part_of = RDF.Uri(self.graph.ns['geolink']+'isPartOf')
        has_part = RDF.Uri(self.graph.ns['geolink']+'hasPart')

        """Delete Dataset identifier

        Find the blank node for the identifier of this dataset and delete
        all statements about it.
        """
        query = u"""DELETE WHERE
        {
            GRAPH <%s>
            {
                <%s> <%s> ?identifier .
                ?identifier ?s ?p
            }
        }
        """ % (self.graph.name, dataset, has_identifier)

        self.graph.update(query)


        """Delete Digital Object identifiers

        Find all Digital Object (through Digital Object isPartOf) identifier
        blank nodes and delete all statements about those blank nodes.
        """
        query = u"""DELETE WHERE
        {
            GRAPH <%s>
            {
                ?digital_object <%s> <%s> .
                ?digital_object <%s> ?identifier .
                ?identifier ?p ?o
            }
        }
        """ % (self.graph.name, is_part_of, dataset, has_identifier)

        self.graph.update(query)


        """Delete Digital Objects

        Find all Digital Object blank nodes (through Dataset hasPart) and
        delete statements about blank nodes.
        """
        query = u"""DELETE WHERE
        {
            GRAPH <%s>
            {
              <%s> <%s> ?digital_object.
              ?digital_object ?p ?o
            }
        }
        """ % (self.graph.name, dataset, has_part)

        self.graph.update(query)


        """Delete statements about the dataset itself"""
        self.delete('d1dataset:'+identifier_esc, '?p', '?o')


        """Delete respective isCreatorOf statements"""
        self.delete('?s', 'geolink:isCreatorOf', '?o')


    def addDigitalObject(self, dataset_identifier, digital_object_identifier):
        try:
            self.addDigitalObjectTriples(dataset_identifier, digital_object_identifier)
        except Exception as e:
            print e


    def addDigitalObjectTriples(self, dataset_identifier, digital_object_identifier):
        if self.model is None:
            raise Exception("Model not found.")

        dataset_identifier_esc = urllib.unquote(dataset_identifier).decode('utf8')
        do_node = RDF.Node(blank=str(uuid.uuid4()))

        # Get data object meta
        data_meta = dataone.getSystemMetadata(digital_object_identifier)

        if data_meta is None:
            raise Exception("System metadata for data object %s was not found. Continuing to next data object." % digital_object_identifier)

        self.add(do_node, 'rdf:type', 'geolink:DigitalObject')
        self.add(do_node, 'geolink:isPartOf', 'd1dataset:'+dataset_identifier_esc)
        self.add('d1dataset:'+dataset_identifier_esc, 'geolink:hasPart', do_node)
        self.addIdentifierTriples(do_node, digital_object_identifier)

        # Checksum and checksum algorithm
        checksum_node = data_meta.find(".//checksum")

        if checksum_node is not None:
            self.add(do_node, 'geolink:hasChecksum', RDF.Node(checksum_node.text))
            self.add(do_node, 'geolink:hasChecksumAlgorithm', RDF.Node(checksum_node.get("algorithm")))
        else:
            raise Exception('Sysmeta XML for PID %s had no checksum element' % digital_object_identifier)

        # Size
        size_node = data_meta.find("./size")

        if size_node is not None:
            self.add(do_node, 'geolink:hasByteLength', RDF.Node(size_node.text))
        else:
            raise Exception('Sysmeta XML for PID %s had no size element' % digital_object_identifier)

        # Format
        format_id_node = data_meta.find("./formatId")

        if format_id_node is not None:
            if format_id_node.text in self.formats:
                self.add(do_node, 'geolink:hasFormat', RDF.Uri(self.formats[format_id_node.text]['uri']))
            else:
                raise Exception('Format %s not found in list of known formats.' % format_id_node.text)
        else:
            raise Exception('Sysmeta XML for PID %s had no formatId element' % digital_object_identifier)

        # Date uploaded
        date_uploaded_node = data_meta.find("./dateUploaded")

        if date_uploaded_node is not None:
            self.add(do_node, 'geolink:dateUploaded', RDF.Node(date_uploaded_node.text))
        else:
            raise Exception('Sysmeta XML for PID %s had no dataUploaded element' % digital_object_identifier)

        # Authoritative MN
        authoritative_mn = data_meta.find("./authoritativeMemberNode")

        if authoritative_mn is not None:
            self.add(do_node, 'geolink:hasAuthoritativeDigitalGraph', 'd1node:' + authoritative_mn.text)
        else:
            raise Exception('Sysmeta XML for PID %s had no authoritativeMemberNode element' % digital_object_identifier)

        # Replica MN's
        replica_mns = data_meta.findall("./replica")

        if replica_mns is None:
            raise Exception('Sysmeta XML for PID %s had no replica element' % digital_object_identifier)

        for replica_mn in replica_mns:
            replica_node = replica_mn.find("./replicaMemberNode")

            if replica_node is not None:
                self.add(do_node, 'geolink:hasReplicaDigitalGraph', 'd1node:' + replica_node.text)
            else:
                raise Exception('Sysmeta XML for PID %s had no replicaMemberNode element' % digital_object_identifier)

        # Origin MN
        origin_mn = data_meta.find("./originMemberNode")

        if origin_mn is not None:
            self.add(do_node, 'geolink:hasOriginDigitalgraph', 'd1node:' + origin_mn.text)
        else:
            raise Exception('Sysmeta XML for PID %s had no originMemberNode element' % digital_object_identifier)

        # Obsoletes (mapped as PROV#wasRevisionOf)
        obsoletes_node = data_meta.find("./obsoletes")

        if obsoletes_node is not None:
            other_document = urllib.unquote(obsoletes_node.text).decode('utf8')
            self.add(do_node, 'prov:wasRevisionOf', 'd1dataset:'+other_document)

        # Submitter and rights holders
        # submitter_node = data_meta.find("./submitter")
        #
        # if submitter_node is not None:
        #     submitter_node_text = " ".join(re.findall(r"o=(\w+)", submitter_node.text, re.IGNORECASE))
        #
        #     if len(submitter_node_text) > 0:
        #         self.insert('d1dataset:'+data_id, 'geolink:hasCreator', ])


        # rights_holder_node = data_meta.find("./rightsHolder")
        #
        # if rights_holder_node is not None:
        #     rights_holder_node_text = " ".join(re.findall(r"o=(\w+)", rights_holder_node.text, re.IGNORECASE))
        #
        #     if len(rights_holder_node_text) > 0:
        #         addStatement(model, d1dataset+data_id, self.graph.ns["geolink"]+"hasRightsHolder", RDF.Uri("urn:node:" + rights_holder_node_text.upper()))


    def addPerson(self, record):
        if record is None:
            return

        logging.info("Calling findPersonURI on %s.", record)
        person_uri = self.findPersonURI(record)

        if person_uri is None:
            person_uri = self.mintPersonPrefixedURIString()
            logging.info("Person was not found. Minted URI of %s", person_uri)

        self.addPersonTriples(person_uri, record)


    def addPersonTriples(self, uri, record):
        if self.model is None:
            raise Exception("Model not found.")

        logging.info("Adding person triples for person with uri '%s' and record '%s'", uri, record)

        self.add(uri, 'rdf:type', 'geolink:Person')

        if 'salutation' in record:
            self.add(uri, 'geolink:namePrefix', record['salutation'])

        if 'full_name' in record:
            self.add(uri, 'geolink:nameFull', record['full_name'])

        if 'first_name' in record:
            self.add(uri, 'geolink:nameGiven', record['first_name'])

        if 'last_name' in record:
            self.add(uri, 'geolink:nameFamily', record['last_name'])

        if 'organization' in record:
            organization_name = record['organization']
            logging.info("Looking up organization with name '%s'", organization_name)

            if self.organizationExists(organization_name):
                logging.info("Organization with name '%s' exists.", organization_name)
                organization_uri = self.findOrganizationURI({'name' : organization_name})
            else:
                organization_uri = self.mintOrganizationPrefixedURIString()
                logging.info("Minted new organization URI of '%s' and adding triples.", organization_uri)
                self.add(organization_uri, 'rdfs:label', organization_name)

            self.add(uri, 'geolink:hasAffiliation', RDF.Uri(organization_uri))

        if 'email' in record:
            self.add(uri, 'foaf:mbox', RDF.Uri('mailto:' + record['email'].lower()))

        if 'address' in record:
            self.add(uri, 'geolink:address', record['address'])

        if 'role' in record and 'document' in record:
            if record['role'] == 'creator':
                self.add(uri, 'geolink:isCreatorOf', 'd1dataset:' + urllib.unquote(record['document']).decode('utf8'))
            elif record['role'] == 'contact':
                self.add(uri, 'geolink:isContactOf', 'd1dataset:' + urllib.unquote(record['document']).decode('utf8'))


    def addOrganization(self, record):
        if record is None:
            return

        logging.info("Calling findOrganizationURI on %s.", record)
        organization_uri = self.findOrganizationURI(record)

        if organization_uri is None:
            organization_uri = self.mintOrganizationPrefixedURIString()
            logging.info("Organization was not found. Minted URI of %s", organization_uri)

        self.addOrganizationTriples(organization_uri, record)


    def addOrganizationTriples(self, uri, record):
        if self.model is None:
            raise Exception("Model not found.")

        logging.info("Adding organization triples for organization with uri '%s' and record '%s'", uri, record)

        self.add(uri, 'rdf:type', 'geolink:Organization')

        if 'name' in record:
            self.add(uri, 'rdfs:label', record['name'])

        if 'email' in record:
            self.add(uri, 'foaf:mbox', RDF.Uri('mailto:' + record['email'].lower()))

        if 'address' in record:
            self.add(uri, 'geolink:address', record['address'])

        if 'role' in record and 'document' in record:
            if record['role'] == 'creator':
                self.add(uri, 'geolink:isCreatorOf', 'd1dataset:' + urllib.unquote(record['document']).decode('utf8'))
            elif record['role'] == 'contact':
                self.add(uri, 'geolink:isContactOf', 'd1dataset:' + urllib.unquote(record['document']).decode('utf8'))


    def findPersonURI(self, record):
        """Find a person record in the graph according to a set of rules
        for matching records.

        A record is said to already exist in the graph if exactly one
        person exists in graph with the same non-zero-length last name and
        email. This is the only rule used right now.

        Arguments:
        ----------
        record : Dict
            A Dictionary of keys for the record ('last_name, 'email', etc.)
        """

        if record is None:
            return None

        logging.info("Looking up person URI for %s", record)

        # Match via last name and email
        if 'last_name' in record and 'email' in record:
            logging.info("Attempting to match %s via last name and email.", record)

            last_name = record['last_name']
            email = record['email']

            if len(last_name) < 1 or len(email) < 1:
                return None

            query_string = u"""
            SELECT ?s
            WHERE {
                ?s rdf:type geolink:Person .
                ?s geolink:nameFamily '''%s''' .
                ?s foaf:mbox <mailto:%s>

            }
            """ % (last_name,
                  email.lower())

            find_result = self.graph.query(query_string)

            if find_result is None or len(find_result) != 1:
                logging.info("No match found.")
                return None

            # Remove < and > around string
            person_uri_string = find_result[0]['s']
            person_uri_string = person_uri_string.replace('<', '')
            person_uri_string = person_uri_string.replace('>', '')

            # Make an RDF.Uri
            person_uri = RDF.Uri(person_uri_string)
            logging.info("Match found %s", person_uri)

            return person_uri

        # Search for existing records that are creators of documents obsoleted
        # by the current one. To do this we query the current model (if it
        # exists) for a prov:wasRevisionOf statement.

        if 'last_name' in record and 'document' in record and self.model is not None:
            logging.info("Attempting to match %s via last name and wasRevisionOf.", record)

            query = RDF.Statement(subject = RDF.Uri(self.graph.ns['d1dataset']+urllib.unquote(record['document']).decode('utf8')),
                                  predicate = RDF.Uri(self.graph.ns['prov']+'wasRevisionOf'))

            revised_documents = []

            for st in self.model.find_statements(query):
                # Only add unique datasets because we end up adding multiple
                # revision statements for the metadata and the digital object
                # Convert the object to a str and remove its namespace prefix
                # first
                object_string = str(st.object).replace(self.graph.ns['d1dataset'], '')

                if object_string not in revised_documents:
                    revised_documents.append(object_string)

            if len(revised_documents) != 1:
                return None

            last_name = RDF.Node(record['last_name'])
            revised_document = RDF.Uri(self.graph.ns['d1dataset'] + revised_documents[0])

            # Query
            query_string = u"""select ?person
            where {
                ?person rdf:type geolink:Person .
                ?person geolink:nameFamily '''%s''' .
                ?person geolink:isCreatorOf <%s> .
            }""" % (last_name, revised_document)

            logging.info("Looking up person with query '%s'.", query_string)
            result = self.graph.query(query_string)

            # Use the person if we find exactly one match
            if len(result) == 1 and 'person' in result[0]:
                logging.info("Person match found.")
                result_string = result[0]['person']
                person_uuid_search = re.search(r"<%s(.*)>" % self.graph.ns['d1person'], result_string)

                if person_uuid_search is None:
                    logging.error("Failed to extract UUID string from result.")
                    return None

                person_uuid = person_uuid_search.group(1)

                return RDF.Uri(self.graph.ns['d1person']+person_uuid)


        return None


    def organizationExists(self, organizationName):
        """Checks if the organization already exists in the graph or not.
        It uses findOrganizationURI method to check if the
        organization URI is in the system or not


        Arguments:
        ----------
        record : Dict
            A Dictionary of keys for the record ('name')

        :return: boolean
            A boolean value representing the existence of organization in the graph
        """
        if len(organizationName) < 1:
            return None

        record = {}
        record["name"] = organizationName
        return True if self.findOrganizationURI(record) == None else False



    def findOrganizationURI(self, record):
        """Find an organization record in the graph according to a set of
        rules for matching records.

        A record is said to already exist in the graph if exactly one
        organization in the graph the same non-zero-length name. This is
        the only rule used right now.

        Arguments:
        ----------
        record : Dict
            A Dictionary of keys for the record ('last_name, 'email', etc.)
        """

        if record is None:
            return None

        if 'name' in record:
            name = record['name']

            if len(name) < 1:
                return None

            query_string = u"""
            SELECT ?s
            WHERE {
                ?s rdf:type geolink:Organization .
                ?s rdfs:label '''%s'''
            }
            """ % name

            logging.info("Looking up organization with query %s", query_string)
            find_result = self.graph.query(query_string)

            if find_result is None or len(find_result) != 1:
                logging.info("Organization not found by name.")
                return None

            # Remove < and > around string
            organization_uri_string = find_result[0]['s']
            organization_uri_string = organization_uri_string.replace('<', '')
            organization_uri_string = organization_uri_string.replace('>', '')

            # Make an RDF.Uri
            organization_uri = RDF.Uri(organization_uri_string)
            logging.info("Found organiztion match for organization URI %s.", organization_uri)

            return organization_uri

        return None


    def mintPersonPrefixedURIString(self):
        new_uuid = str(uuid.uuid4())
        uri_string = "d1person:urn:uuid:%s" % new_uuid

        return uri_string


    def mintOrganizationPrefixedURIString(self):
        new_uuid = str(uuid.uuid4())
        uri_string = "d1org:urn:uuid:%s" % new_uuid

        return uri_string


    def addIdentifierTriples(self, node, identifier):
        """Add triples for the given identiifer to the given node."""

        if self.model is None:
            raise Exception("Model not found.")

        scheme = util.getIdentifierScheme(identifier)
        resolve_url = util.getIdentifierResolveURL(identifier)

        # Create a blank node for the identifier
        identifier_node = RDF.Node(blank=str(uuid.uuid4()))

        self.add(node, 'geolink:hasIdentifier', identifier_node)
        self.add(identifier_node, 'rdf:type', 'geolink:Identifier')
        self.add(identifier_node, 'rdfs:label', RDF.Node(identifier))

        self.add(identifier_node, 'geolink:hasIdentifierValue', RDF.Node(identifier))
        self.add(identifier_node, 'geolink:hasIdentifierScheme', 'datacite:'+scheme)

        if resolve_url is not None:
            self.add(identifier_node, 'geolink:hasIdentifierResolveURL', RDF.Uri(resolve_url))

        # Also always add the DataOne resolve URL for non local-resource-identifier-scheme identifiers
        if scheme != 'local-resource-identifier-scheme':
            dataone_resolve_url = 'https://cn.dataone.org/cn/v1/resolve/%s' % urllib.unquote(identifier).decode('utf8')
            self.add(identifier_node, 'geolink:hasIdentifierResolveURL', RDF.Uri(dataone_resolve_url))


    def tripleHasBlankNode(self, s , p , o):
        """

        s : RDF.Node | str
            The subject of the triple pattern.

        p : RDF.Node | str
            The predicate of the triple pattern.

        o : RDF.Node | str
            The object of the triple pattern.

        :return:
            A boolean value indicating whether either of the s / p / o is a blank node or not
        """

        # Check for blank nodes:
        if isinstance(s, RDF.Node):
            if s.is_blank():
                return True
        elif isinstance(s, str):
            if s.startswith("_:"):
                return True


        if isinstance(p, RDF.Node):
            if p.is_blank():
                return True
        elif isinstance(p, str):
            if p.startswith("_:"):
                return True

        if isinstance(o, RDF.Node):
            if o.is_blank():
                return True
        elif isinstance(o, str):
            if o.startswith("_:"):
                return True

        return  False
