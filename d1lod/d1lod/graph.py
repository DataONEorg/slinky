"""d1lod.graph

This is a utility module for the d1lod service to read and write d1lod contents
to the Virtuoso graphs. It contains the following functionality:

01. CREATE operation Creating a new graph in stores that support empty graphs.
02. DELETE operation Removing a graph and all of its contents.
03. COPY operation Modifying a graph to contain a copy of another.
04. MOVE  operation Moving all of the data from one graph into another.
05. ADD operation Reproducing all data from one graph into another.
06. Getting a list of all the graphs.
07. Insertion of some triples, given inline in the request, into a graph
08. Deletion of some triples, given inline in the request, if the respective graph contains those
09. Loading of the contents of a document representing a graph into a graph
10. Clearing of all the triples in (one or more) graphs.
11. Conditional Insert / delete of d1lod contents
12. Retreiving contents of a graph

"""

import requests
import RDF
import json
import logging
import xml.etree.ElementTree as ET


class Graph:
    def __init__(self, host, port, name, ns={}):
        self.name = name
        self.ns = ns
        self.host = host
        self.port = port
        self.endpoints = {
            'sparql': 'http://%s:%s/sparql' % (self.host, self.port),
        }

        # Set aside a Session object
        # We use this when making HTTP requests to reduce overhead when making
        # many requests during the lifetime of a Graph objects
        self.session = requests.Session()


    def __str__(self):\
        return "Graph: '%s'" % self.name


    ###########################################################
    # The following section contains methods to CRUD graphs   #
    ###########################################################


    def create_graph(self, silent=False):
        """This operation creates a graph in the Virtuoso Store.

        Arguments:
        ----------

        silent: boolean
            If the SILENT flag is enabled, then FAILURE will not be returned,
            even if there are errors while creating the graph.
            By default it is set to False.


        Returns: None."""
        if self.exists() == "false":
            logging.info("Creating graph - " + self.name)
            if not silent:
                create_query = "CREATE GRAPH <" + self.name + ">"
            else:
                create_query = "CREATE SILENT GRAPH <" + self.name + ">"
            sparqlResponse = self.query(query_string=create_query, accept='text/plain')
            logging.info(sparqlResponse)
        else:
            logging.info("Graph already exists!")

        return


    def delete_graph(self, silent=False):
        """This operation deletes a graph from the Virtuoso Store.
        TODO: deletes only empty graphs

        Arguments:
        ----------

        silent: boolean
            If the SILENT flag is enabled, then FAILURE will not be returned,
            even if there are errors while deleting the graph
            By default it is set to False.

        Returns: None."""
        if self.exists() == "true":
            logging.info("Deleting graph - " + self.name)
            if not silent:
                delete_query = "DROP GRAPH <" + self.name + ">"
            else:
                delete_query = "DROP SILENT GRAPH <" + self.name + ">"
            sparqlResponse = self.query(query_string=delete_query, accept='text/plain')
            logging.info(sparqlResponse)
        else:
            logging.info("Graph does not exist!")

        return


    def copy_graph(self, target_graph_name, silent=False):
        """The COPY operation is a shortcut for inserting all data from an input graph into a destination graph.
        Data from the input graph is not affected, but data from the destination graph,
        if any, is removed before insertion.

        Arguments:
        ----------

        target_graph_name: str
            the <URI> of the destination graph

        silent: boolean
            If the SILENT flag is enabled, then FAILURE will not be returned,
            even if there are errors while copying triples from the source to the destination
            By default it is set to False.

        Returns: None."""
        if self.exists() == "true":
            logging.info("Copying source graph - " + self.name + " to the destination graph - " + target_graph_name)
            if not silent:
                copy_query = """
                COPY GRAPH <%s> TO GRAPH <%s>
                """ % (self.name, target_graph_name)

            else:
                copy_query = """
                COPY SILENT GRAPH <%s> TO GRAPH <%s>
                """ % (self.name, target_graph_name)
            sparqlResponse = self.query(query_string=copy_query, accept='text/plain')
            logging.info(sparqlResponse)
        else:
            logging.info("Source Graph does not exists!")

        return


    def move_graph(self, target_graph_name, silent=False):
        """The MOVE operation is a shortcut for moving all data from an input graph into a destination graph.
        The input graph is removed after insertion and data from the destination graph,
        if any, is removed before insertion.

        Arguments:
        ----------

        target_graph_name: str
            the <URI> of the destination graph

        silent: boolean
            If the SILENT flag is enabled, then FAILURE will not be returned,
            even if there are errors while moving from the source to the destination
            By default it is set to False.

        Returns: None."""
        if self.exists() == "true":
            logging.info("Moving source graph - " + self.name + " to the destination graph - " + target_graph_name)
            if not silent:
                move_query = """
                MOVE GRAPH <%s> TO GRAPH <%s>
                """ % (self.name, target_graph_name)
            else:
                move_query = """
                MOVE SILENT GRAPH <%s> TO GRAPH <%s>
                """ % (self.name, target_graph_name)
            sparqlResponse = self.query(query_string=move_query, accept='text/plain')
            logging.info(sparqlResponse)
        else:
            logging.info("Source Graph does not exists!")

        return


    def add_graph(self, target_graph_name, silent=False):
        """The ADD operation is a shortcut for inserting all data from an input graph into a destination graph.
         Data from the input graph is not affected, and initial data from the destination graph,
         if any, is kept intact.

        Arguments:
        ----------

        target_graph_name: str
            the <URI> of the destination graph

        silent: boolean
            If the SILENT flag is enabled, then FAILURE will not be returned,
            even if there are errors while adding the triples from the source to the destination
            By default it is set to False.

        Returns: None."""
        if self.exists() == "true":
            logging.info("Adding source graph - " + self.name + " to the destination graph - " + target_graph_name)
            if not silent:
                add_query = """
                ADD GRAPH <%s> TO GRAPH <%s>
                """ % (self.name, target_graph_name)
            else:
                add_query = """
                ADD SILENT GRAPH <%s> TO GRAPH <%s>
                """ % (self.name, target_graph_name)
            sparqlResponse = self.query(query_string=add_query, accept='text/plain')
            logging.info(sparqlResponse)
        else:
            logging.info("Source Graph does not exists!")

        return

    ##########################################################################
    # The following section contains methods to update data within a graph   #
    ##########################################################################


    def insert(self, s, p, o, context=None):
        """Insert a triple using a SPARQL UPDATE query.

        Arguments:
        ----------
        s : (RDF.Node / RDF.Uri, str
        p : (RDF.Node / RDF.Uri, str
        o : (RDF.Node / RDF.Uri, str

        context : str
            (optional) Name of the context to execute the query against
            
        Returns: dictionary object of the SPARQL response
        """

        # checks if the payload contains a blank node or not
        blank_node = self.tripleHasBlankNode(s, p, o)

        subj_string = self.term_to_sparql(s)
        pred_string = self.term_to_sparql(p)
        obj_string = self.term_to_sparql(o)
        payload_string = subj_string + " " + pred_string + " " + obj_string

        return (self.insert_data(payload=payload_string, blank_node=blank_node))


    def insert_data(self, payload='', prefix='', blank_node=False):
        """The INSERT DATA operation adds some triples, given inline in the request, into a graph.
        This should create the destination graph if it does not exist. If the graph does not exist
        and it can not be created for any reason, then a failure must be returned.

        Arguments:
        ----------

        payload: str
            contents / triples to be loaded in the string

        prefix: str
            prefixes used


        Returns: dictionary object of the SPARQL response.
        """
        if self.name is None:
            graph_name = self.name
        insert_query = """
        INSERT
        {
            GRAPH <%s>
            {
                %s
            }
        }
        """ % (self.name, payload)

        return (self.query(query_string=insert_query, blank_node=blank_node))


    def delete_data(self, payload='', prefix='', blank_node=False):
        """The DELETE DATA operation deletes some triples, given inline in the request, into a graph.
        If the graph does not exist and it can not be created for any reason, then a failure must be returned.

        Arguments:
        ----------

        payload: str
            contents / triples to be loaded in the string

        prefix: str
            prefixes used


        Returns: dictionary object of the SPARQL response
        """
        if self.name == None:
            graph_name = self.name

        delete_query = """
        DELETE WHERE
        {
            GRAPH <%s>
            {
                %s
            }
        }
        """ % (self.name, payload)
        sparqlResponse = self.query(query_string=delete_query, blank_node=blank_node)
        return (sparqlResponse)


    def clear(self, blank_node=False):
        """The DROP DATA operation keeps the graph and deletes the existing statements in the graph
        If the graph does not exist the call does not give any error

        Arguments:
        ----------

        graph_name: str
            the <URI> of the graph

        payload: str
            contents / triples to be loaded in the string

        prefix: str
            prefixes used


        Returns: dictionary object of the SPARQL response
        """
        delete_query = """
        DROP SILENT GRAPH <%s>
        """ % (self.name)
        
        sparqlResponse = self.query(query_string=delete_query, blank_node=blank_node)
        return (sparqlResponse)


    ##################################################################################################
    # The following section contains various utility functions to perform CRUD on Virtuoso graphs    #
    ##################################################################################################


    def namespacePrefixString(self):
        """Generate a string of namespaces suitable for appending to the front
        of a SPARQL QUERY, i.e.,

            @prefix x: <http://x.com> .
            @prefix y: <http://y.com> .

        Returns: (str) Newline-separated @prefix: <x> . string.
        """

        ns = self.ns

        ns_strings = []

        for key in ns:
            ns_strings.append("PREFIX %s:<%s>" % (key, ns[key]))

        return "\n".join(ns_strings)


    def query(self, query_string, blank_node=False, accept='application/json'):
        """Execute a SPARQL QUERY against the Graph.

        Arguments:
        ----------

        query_string : str
            SPARQL query string.

        accept : str
            An appropriate HTTP Accept header value. Defaults to JSON.

        formatResponse: boolean
            A boolean value indicating the formatting requirements of the results.


        Returns: A result dict containing the query response."""

        # getrting the namespaces before performing the query
        prefix = self.namespacePrefixString()

        results = {}
        endpoint = self.endpoints['sparql']
        params = {
            'query': prefix + "\n" + query_string
        }

        r = self.session.post(endpoint, params=params, auth=('dba', 'dev.nceas'),headers={'Connection':'close'})

        logging.info(prefix + "\n" + query_string)

        if r.status_code != 200:
            logging.error("SPARQL QUERY failed. Status was not 200 as expected.")
            logging.error(r.status_code)
            logging.error(r.text)
            logging.error(query_string)

        if r.headers['Content-Type'] == "application/sparql-results+xml; charset=UTF-8":
            response_type = "xml"
            response_var = r.content
            results = self.processResponse(response_var, response_type)

        elif r.headers['Content-Type'] == "application/json":
            try:
                response_type = "json"
                response_var = r.json()
                results = self.processResponse(response_var, response_type)
            except:
                logging.error("Failed to convert response to JSON.")
                logging.error(r.status_code)
                logging.error(r.text)
                results = {}

        return results


    def processResponse(self, response_var, response_type):
        """Process a JSON response from the Graph and create a friendlier
        format. The format is a list of Dicts, where the names in each dict
        match the bindings of the query.
        """
        results = []

        if response_type == "xml":
            response_content = ET.fromstring(response_var)

            xml_result_element = []
            xml_results_element = None
            xml_result = []

            for child in response_content:
                if child.tag == '{http://www.w3.org/2005/sparql-results#}head':
                    xml_head_element = child
                elif child.tag == '{http://www.w3.org/2005/sparql-results#}results':
                    xml_results_element = child
                else:
                    pass

            for child in xml_results_element:
                if child.tag == '{http://www.w3.org/2005/sparql-results#}result':
                    xml_result_element.append(child)

            xml_result = []
            for result in xml_result_element:
                for binding in result:
                    xml_result_dict = {}
                    binding_key = binding.attrib["name"]
                    binding_val = None
                    for uri in binding:
                        binding_val = uri.text
                    xml_result_dict[binding_key] = binding_val
                    xml_result.append(xml_result_dict)

            results = xml_result

        else:
            response = response_var

            if 'head' not in response['sparql'] or 'results' not in response['sparql'] \
                    or 'result' not in response['sparql']['results'] \
                    or 'binding' not in response['sparql']['results']['result']:
                return results

            for binding in response['sparql']['results']['result']['binding']:
                row = {}

                row[binding["@name"]] = binding["uri"]

                results.append(row)

        return results


    def term_to_sparql(self, term):
        """Convert an RDF term to a suitable string to be inserted into a
        SPARQL query.
        """

        if isinstance(term, str):
            # Do nothing to bindings
            if term.startswith('?'):
                return term
            else:
                return "%s" % term
        elif isinstance(term, RDF.Node):
            if term.is_resource():
                return "<%s>" % str(term)
            else:
                return "%s" % str(term)
        elif isinstance(term, RDF.Uri):
            return "<%s>" % str(term)


    def update(self, query_string):
        """Execute a SPARQL UPDATE query against the graph.

        Arguments:
        ----------

        query_string : str
            SPARQL query string.
            
        Returns: HTTP response from the database
        """

        # getrting the namespaces before performing the query
        prefix = self.namespacePrefixString()

        query_string = prefix + "\n" + query_string

        endpoint = self.endpoints['sparql']

        r = self.session.post(endpoint, data={'update': query_string.strip()},headers={'Connection':'close'})

        if r.status_code != requests.codes.ok:
            logging.error("SPARQL UPDATE failed. Status was not 201 as expected.")
            logging.error(endpoint)
            logging.error(r.text)
            logging.error(query_string)

        return r


    def etree_to_dict(self, t):
        """
        Converts the input XML tree to a dictionary object.
        
        Arguments:
        ----------
        
        t: XML objects
            XML tree to be converted to a dictionary
        
        Returns: dictionary object
        """
        return {t.tag: list(map(self.etree_to_dict, t.iterchildren())) or t.text}


    def tripleHasBlankNode(self, s, p, o):
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

        return False


    def graphs(self):
        """
        Get dictinct existing graphs from the Virtuoso store
        
        Returns:
            A list of graphs within the Virtuoso database
        """
        query_string = """
        SELECT DISTINCT ?g WHERE { GRAPH ?g { ?s ?p ?o } }
        """
        response = self.query(query_string)

        # Parsing the result dict and forming array of existing graphs
        repo_list = []
        for i in response:
            repo_list.append(i["g"])

        return repo_list


    def size(self):
        """
        Returns the size of the graph.
        If the graph has no statements then  this function returns 0
        
        Returns:
            [int] size of the graph.
        """
        graph_size = 0
        size_query = """
        SELECT (COUNT(?s) AS ?triples) WHERE { GRAPH <%s> { ?s ?p ?o } }
        """ % (self.name)

        response = self.query(size_query)

        for i in response:
            graph_size = int(i["triples"])
        return graph_size


    def exists(self):
        """Execute a SPARQL QUERY against the Graph.

        Arguments:
        ----------

        None


        Returns: A boolean value representing the existence of the Graph.
        """
        query_string = """ASK WHERE { GRAPH <%s> { } }""" % (self.name)

        endpoint = self.endpoints['sparql']
        params = {
            'query': query_string
        }

        sparqlResponse = self.session.post(endpoint, params=params, auth=('dba', 'dev.nceas'),headers={'Connection':'close'})
        return sparqlResponse.content
