"""d1lod.virtuoso.graphutil

This is a utility module for the d1lod service to read and write d1lod contents
to the Virtuoso graphs. It contains the following functionality:

1. Insertion of some triples, given inline in the request, into a graph
2. Deletion of some triples, given inline in the request, if the respective graph contains those
3. Loading of the contents of a document representing a graph into a graph
4. Clearing of all the triples in (one or more) graphs.
5. Conditional Insert / delete of d1lod contents
6. Retrieving contents of a graph

"""

import requests



class GraphUtil:
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
        return "Repository: '%s'" % self.name


    def exists(self):
        """Execute a SPARQL QUERY against the Graph.

        Arguments:
        ----------

        None


        Returns: A boolean value representing the existence of the Graph."""
        query_string = "ASK WHERE { GRAPH <Bookstore> { ?s ?p ?o } }"
        sparqlResponse = self.query(query_string=query_string, accept='text/plain', formatResponse=False)
        return sparqlResponse.content



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

        headers = { 'Accept': accept}
        results = {}
        endpoint = self.endpoints['sparql']
        params = {
            'default-graph-uri': '',
            'query': query_string

        }

        r = self.session.get(endpoint, headers=headers, params=params, auth=('dba', ''))

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
    graph1 = GraphUtil("localhost", "8890", "BookStore")
    print graph1.exists()