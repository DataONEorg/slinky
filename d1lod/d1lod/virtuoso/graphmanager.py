"""d1lod.virtuoso.graphmanager

This is a graph manager for the d1lod service to manage the Virtuoso graphs.
It contains the following functionality:

1. CREATE operation Creating a new graph in stores that support empty graphs.
2. DELETE operation Removing a graph and all of its contents.
3. COPY operation Modifying a graph to contain a copy of another.
4. MOVE  operation Moving all of the data from one graph into another.
5. ADD operation Reproducing all data from one graph into another.

"""

import requests
import logging


class GraphManager:
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
        # many requests during the lifetime of a Repository objects
        self.session = requests.Session()


    def __str__(self):
        return "Graph: '%s'" % self.name


    def exists(self, graph_name):
        """Execute a SPARQL QUERY against the Graph.

        Arguments:
        ----------

        graph_name: str
            the <URI> to of the graph to check its existence

        Returns: A boolean value representing the existence of the Graph."""
        query_string = "ASK WHERE { GRAPH <" + graph_name + "> { ?s ?p ?o } }"
        sparqlResponse = self.query(query_string=query_string, accept='text/plain', formatResponse=False)
        return sparqlResponse.content


    def create_graph(self, graph_name, silent=False):
        """This operation creates a graph in the Graph Store.

        Arguments:
        ----------

        graph_name: str
            the <URI> to be used to create the graph

        silent: boolean
            If the SILENT flag is enabled, then FAILURE will not be returned,
            even if there are errors while creating the graph.
            By default it is set to False.


        Returns: None."""
        if self.exists(graph_name) == "false":
            print "Creating graph - " + graph_name
            if not silent:
                create_query = "CREATE GRAPH <" + graph_name + ">"
            else:
                create_query = "CREATE SILENT GRAPH <" + graph_name + ">"
            sparqlResponse = self.query(query_string=create_query, accept='text/plain', formatResponse=False)
            print sparqlResponse.content
        else:
            print "Graph already exists!"

        return


    def delete_graph(self, graph_name, silent=False):
        """This operation deletes a graph from the Graph Store.
        TODO: deletes only empty graphs

        Arguments:
        ----------

        graph_name: str
            the <URI> of the graph to be deleted

        silent: boolean
            If the SILENT flag is enabled, then FAILURE will not be returned,
            even if there are errors while deleting the graph
            By default it is set to False.

        Returns: None."""
        if self.exists(graph_name) == "true":
            print "Deleting graph - " + graph_name
            if not silent:
                delete_query = "DROP GRAPH <" + graph_name + ">"
            else:
                delete_query = "DROP SILENT GRAPH <" + graph_name + ">"
            sparqlResponse = self.query(query_string=delete_query, accept='text/plain', formatResponse=False)
            print sparqlResponse.content
        else:
            print "Graph does not exists!"

        return


    def copy_graph(self, source_graph_name, target_graph_name, silent=False):
        """The COPY operation is a shortcut for inserting all data from an input graph into a destination graph.
        Data from the input graph is not affected, but data from the destination graph,
        if any, is removed before insertion.

        Arguments:
        ----------

        source_graph_name: str
            the <URI> of the source graph

        target_graph_name: str
            the <URI> of the destination graph

        silent: boolean
            If the SILENT flag is enabled, then FAILURE will not be returned,
            even if there are errors while copying triples from the source to the destination
            By default it is set to False.

        Returns: None."""
        if self.exists(source_graph_name) == "true":
            print "Copying source graph - " + source_graph_name + " to the destination graph - " + target_graph_name
            if not silent:
                copy_query = "COPY GRAPH <" + source_graph_name + "> TO GRAPH <" + target_graph_name + ">"
            else:
                copy_query = "COPY SILENT GRAPH <" + source_graph_name + "> TO GRAPH <" + target_graph_name + ">"
            sparqlResponse = self.query(query_string=copy_query, accept='text/plain', formatResponse=False)
            print sparqlResponse.content
        else:
            print "Source Graph does not exists!"

        return


    def move_graph(self, source_graph_name, target_graph_name, silent=False):
        """The MOVE operation is a shortcut for moving all data from an input graph into a destination graph.
        The input graph is removed after insertion and data from the destination graph,
        if any, is removed before insertion.

        Arguments:
        ----------

        source_graph_name: str
            the <URI> of the source graph

        target_graph_name: str
            the <URI> of the destination graph

        silent: boolean
            If the SILENT flag is enabled, then FAILURE will not be returned,
            even if there are errors while moving from the source to the destination
            By default it is set to False.

        Returns: None."""
        if self.exists(source_graph_name) == "true":
            print "Moving source graph - " + source_graph_name + " to the destination graph - " + target_graph_name
            if not silent:
                move_query = "MOVE GRAPH <" + source_graph_name + "> TO GRAPH <" + target_graph_name + ">"
            else:
                move_query = "MOVE SILENT GRAPH <" + source_graph_name + "> TO GRAPH <" + target_graph_name + ">"
            sparqlResponse = self.query(query_string=move_query, accept='text/plain', formatResponse=False)
            print sparqlResponse.content
        else:
            print "Source Graph does not exists!"

        return


    def add_graph(self, source_graph_name, target_graph_name, silent=False):
        """The ADD operation is a shortcut for inserting all data from an input graph into a destination graph.
         Data from the input graph is not affected, and initial data from the destination graph,
         if any, is kept intact.

        Arguments:
        ----------

        source_graph_name: str
            the <URI> of the source graph

        target_graph_name: str
            the <URI> of the destination graph

        silent: boolean
            If the SILENT flag is enabled, then FAILURE will not be returned,
            even if there are errors while adding the triples from the source to the destination
            By default it is set to False.

        Returns: None."""
        if self.exists(source_graph_name) == "true":
            print "Adding source graph - " + source_graph_name + " to the destination graph - " + target_graph_name
            if not silent:
                add_query = "ADD GRAPH <" + source_graph_name + "> TO GRAPH <" + target_graph_name + ">"
            else:
                add_query = "ADD SILENT GRAPH <" + source_graph_name + "> TO GRAPH <" + target_graph_name + ">"
            sparqlResponse = self.query(query_string=add_query, accept='text/plain', formatResponse=False)
            print sparqlResponse.content
        else:
            print "Source Graph does not exists!"

        return



    def query(self, query_string, accept='application/json', formatResponse=True):
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

        headers = {'Accept': accept}
        results = {}
        endpoint = self.endpoints['sparql']
        params = {
            'default-graph-uri': '',
            'query': query_string

        }

        r = self.session.get(endpoint, headers=headers, params=params, auth=('dba', 'dev.nceas'))

        if r.status_code != 200:
            print "SPARQL QUERY failed. Status was not 200 as expected."
            print r.status_code
            print r.text
            print query_string

        if formatResponse:
            try:
                results = r.json()
            except:
                print "Failed to convert response to JSON."
                print r.status_code
                print r.text
                return []
            return results

        return r


if __name__ == "__main__":
    graph1 = GraphManager("localhost", "8890", "BookStore")
    graph1.add_graph("Bookstore", "Bookstore3")
