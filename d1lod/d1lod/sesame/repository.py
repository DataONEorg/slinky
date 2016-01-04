"""d1lod.sesame.repository

A Repository is a light-weight wrapper around the Sesame API concerning
Repositories. When a Repository is created, it checks for the existence of
itself and will create the Repository if needed it doesn't exist. A GraphDB Lite
Repository is created by default using the default settings.


Reference material:

http://rdf4j.org/sesame/2.7/docs/system.docbook?view#The_Sesame_Server_REST_API
http://docs.s4.ontotext.com/display/S4docs/Fully+Managed+Database#FullyManagedDatabase-cURL%28dataupload%29
"""

import requests
import RDF


class Repository:
    def __init__(self, store, name, ns={}):
        self.store = store
        self.name = name
        self.ns = ns
        self.endpoints = {
            'size': 'http://%s:%s/openrdf-sesame/repositories/%s/size' % (self.store.host, self.store.port, self.name),
            'statements': 'http://%s:%s/openrdf-sesame/repositories/%s/statements' % (self.store.host, self.store.port, self.name),
            'namespaces': 'http://%s:%s/openrdf-sesame/repositories/%s/namespaces' % (self.store.host, self.store.port, self.name),
            'query': 'http://%s:%s/openrdf-sesame/repositories/%s' % (self.store.host, self.store.port, self.name),
            'contexts': 'http://%s:%s/openrdf-sesame/repositories/%s/rdf-graphs' % (self.store.host, self.store.port, self.name)
        }

        # Set aside a Session object
        # We use this when making HTTP requests to reduce overhead when making
        # many requests during the lifetime of a Repository objects
        self.session = requests.Session()

        # Check if repository exists. Create if it doesn't.
        if not self.exists():
            print "Creating repository '%s'." % name
            self.store.createRepository(name)

        # Add namespaces to existing set
        # Add namespaces
        for prefix in ns:
            print "Adding namespace: @prefix %s: <%s>" % (prefix, ns[prefix])
            self.addNamespace(prefix, ns[prefix])


    def __str__(self):
        return "Repository: '%s'" % self.name


    def exists(self):
        repo_ids = self.store.repositories()

        if repo_ids is None:
            return False

        if self.name in repo_ids:
            return True
        else:
            return False


    def size(self):
        """Get the size the repository (statements).

        Returns: int
            -1: if error
            >= 0: if no error
        """

        endpoint = self.endpoints['size']

        r = self.session.get(endpoint)

        # Handle a common error message
        if r.text.startswith("Unknown repository:"):
            return -1

        # Default return value
        repo_size = -1

        # Try to parse the message as a number and fail gracefully if we can't
        # parse it
        try:
            repo_size = int(r.text)
        except:
            print "Failed to get repo size."
            print r.text

        return repo_size


    def clear(self):
        """Clear the repository of all statements."""

        response = None

        try:
            response = self.session.delete(self.endpoints['statements'])
        except:
            print "Failed to clear repository."

        if response is None or response.status_code >= 300:
            print "Something went wrong when deleting all statements from the repository."
            print response.text


    def import_from_string(self, text, fmt='rdfxml', context=None):
        """Import a string containing RDF into the repository.

        Arguments:
        ----------

        text : str
            RDF/XML or Turtle-serialized RDF.

        fmt : str (Optional)
            Short-hand name of the contnet type. Accepts one of [turtle rdfxml].

        context : str (Optional)
            Name for the context.


        Returns: The request object
        """

        # Process the format argument
        if fmt == 'turtle':
            content_type = 'text/turtle'
        elif fmt == 'rdfxml':
            content_type = 'application/rdf+xml'
        else:
            print "Format of %s not supported. Exiting." % fmt

        # Decide which endpoint we need to use
        if context is None:
            endpoint = self.endpoints['statements']
        else:
            endpoint = self.endpoints['contexts'] + '/' + context

        # Prepare and make the request
        headers = {
            'Content-Type': content_type,
            'charset': 'UTF-8'
        }

        r = self.session.post(endpoint, headers=headers, data=text.encode('utf-8'))

        if r.status_code != 204:
            print "Failed to import file %s." % filename
            print endpoint
            print headers
            print r.status_code
            print r.text

        return r


    def import_from_file(self, filename, fmt='rdfxml', context=None):
        """Import a file containing RDF into the repository.

        Note that this passes a file handle to the request module call to post()
        so this is slightly different than just passing the file's contents as
        a string.


        Arguments:
        ----------

        text : str
            RDF/XML or Turtle-serialized RDF.

        fmt : str (Optional)
            Short-hand name of the contnet type. Accepts one of [turtle rdfxml].

        context : str (Optional)
            Name for the context.


        Returns: The request object
        """

        # Process the format argument
        if fmt == 'turtle':
            content_type = 'text/turtle'
        elif fmt == 'rdfxml':
            content_type = 'application/rdf+xml'
        else:
            print "Format of %s not supported. Exiting." % fmt

        # Decide which endpoint we need to use
        if context is None:
            endpoint = self.endpoints['statements']
        else:
            endpoint = self.endpoints['contexts'] + '/' + context

        # Prepare and make the request
        headers = {
            'Content-Type': content_type,
            'charset': 'UTF-8'
        }

        r = self.session.post(endpoint, headers=headers, data=open(filename, 'rb'))

        if r.status_code != 204:
            print "Failed to import file %s." % filename
            print endpoint
            print headers
            print r.status_code
            print r.text

        return r


    def export(self, fmt='turtle', context=None):
        """Export RDF from the repository in the specified format.

        Arguments:
        ----------

        text : str
            RDF/XML or Turtle-serialized RDF.

        fmt : str (Optional)
            Short-hand name of the contnet type. Accepts one of [turtle rdfxml].

        context : str (Optional)
            Name for the context.


        Returns: (str) Text of the RDF serialized in the appropriate format.
        """

        # Process the format argument
        if fmt == 'turtle':
            accept = 'text/turtle'
        elif fmt == 'rdfxml':
            accept = 'application/rdf+xml'
        else:
            print "Format of %s is not yet implemented. Doing nothing." % fmt
            return

        # Decide which endpoint we need to use
        if context is None:
            endpoint = self.endpoints['statements']
        else:
            endpoint = self.endpoints['contexts'] + '/' + context

        # Prepare and make the request
        headers = {
            'Accept': accept
        }

        params = {
            'infer': 'false'
        }

        r = self.session.get(endpoint, headers=headers, params=params)

        return r.text


    def contexts(self):
        """Get a list of contexts from the Repository.

        Returns: (list) List of context names.
        """
        headers = { "Accept": "application/json" }
        endpoint = self.endpoints['contexts']

        r = self.session.get(endpoint, headers=headers)

        return self.processJSONResponse(r.json())


    def namespaces(self):
        """Get a list of the namespaces this repository knows about.

        Return: (Dict) prefix:ns mappings.
        """

        headers = { "Accept": "application/json" }
        endpoint = self.endpoints['namespaces']

        r = self.session.get(endpoint, headers=headers)

        if r.text.startswith("Unknown repository:"):
            return {}

        if r.status_code != 200:
            print "Failed to retrieve namespaces."
            print r.text
            return {}

        response =  r.json()
        bindings = response['results']['bindings']

        namespaces = {}

        for binding in bindings:
            prefix = binding['prefix']['value']
            namespace = binding['namespace']['value']

            namespaces[prefix] = namespace

        return namespaces


    def getNamespace(self, prefix):
        """Retrieve a namespace from the Repository's set of namespaces.

        Arguments:
        ----------

        prefix: str
            Name of the prefix

        Returns: (str) Namespace of the given prefix. None if not found.
        """

        ns = self.namespaces()

        if prefix in ns:
            return ns[prefix]
        else:
            return None


    def addNamespace(self, namespace, value):
        """Add a namespace to the repository.

        Arguments:
        ----------

        namespace : str
            Prefix string for the namespace.

        value : str
            URI for the namespace prefix.


        Returns: The request object.
        """

        endpoint = self.endpoints['namespaces'] + '/' + namespace

        r = self.session.put(endpoint, data = value)

        if r.status_code != 204:
            print "Adding namespace failed."
            print "Status Code: %d." % r.status_code
            print r.text

        return r


    def removeNamespace(self, namespace):
        """Remove a namespace from the repository.

        Arguments:
        ----------

        namespace : str
            Prefix string for the namespace.


        Returns: The request object.
        """

        endpoint = self.endpoints['namespaces']

        r = self.session.delete(endpoint)

        if r.status_code != 204:
            print "Removing namespace failed."
            print "Status Code: %d." % r.status_code
            print r.text

        return r


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


    def query(self, query_string, accept='application/json'):
        """Execute a SPARQL QUERY against the Repository.

        Arguments:
        ----------

        query_string : str
            SPARQL query string.

        accept : str
            An appropriate HTTP Accept header value. Defaults to JSON.


        Returns: A result as a List of Dicts where the Dicts contain bindings
        to the variables in the query string."""

        headers = { 'Accept': accept }
        endpoint = self.endpoints['query']
        params = {
            'queryLn': 'SPARQL',
            'query': self.namespacePrefixString() + query_string.strip(),
            'infer': 'false'
        }

        r = self.session.get(endpoint, headers=headers, params=params)

        if r.status_code != 200:
            print "SPARQL QUERY failed. Status was not 200 as expected."
            print r.status_code
            print r.text
            print query_string

        try:
            response_json = r.json()
        except:
            print "Failed to convert response to JSON."
            print r.status_code
            print r.text
            return []

        results = self.processJSONResponse(response_json)

        return results


    def update(self, query_string):
        """Execute a SPARQL UPDATE query against the repository.

        Arguments:
        ----------

        query_string : str
            SPARQL query string.
        """

        endpoint = self.endpoints['statements']

        r = self.session.post(endpoint, data={ 'update': query_string.strip() })

        if r.status_code != 204:
            print "SPARQL UPDATE failed. Status was not 204 as expected."
            print endpoint
            print r.text
            print query_string

        return r


    def count(self):
        """Count the number of triples in the repository with the given pattern.

        Parameters:
        -----------

        s : RDF.Node
            The subject of the triple pattern.

        p : RDF.Node
            The predicate of the triple pattern.

        o : RDF.Node
            The object of the triple pattern.

        Returns:
        --------

        int
            TODO
        """

        query = u'SELECT (COUNT(*) AS ?count) { ?s ?p ?o }'
        result = self.query(query)

        if result is None:
            return -1

        if len(result) > 0 and 'error-message' in result[0]:
            print result[0]['error-message']
            return -1

        if 'count' not in result[0]:
            print result
            return -1

            return result[0]['count']


    def insert(self, s, p, o, context=None):
        """Insert a triple using a SPARQL UPDATE query.

        Arguments:
        ----------
        s : (RDF.Node / RDF.Uri, str
        p : (RDF.Node / RDF.Uri, str
        o : (RDF.Node / RDF.Uri, str

        context : str
            (optional) Name of the context to execute the query against
        """

        subj_string = self.term_to_sparql(s)
        pred_string = self.term_to_sparql(p)
        obj_string = self.term_to_sparql(o)

        if context is not None:
            query = """
            INSERT DATA {
                GRAPH <%s/%s> {
                    %s %s %s
                }
            }
            """ % (self.endpoints['contexts'], context, subj_string, pred_string, obj_string)
        else:
            query = """
            INSERT DATA { %s %s %s }
            """ % (subj_string, pred_string, obj_string)


        return self.update(query)


    def delete_triples_about(self, subject, context=None):
        """Delete triples about the given subject using a SPARQL UPDATE
        query.

        Arguments:
        ----------
        subject : RDF.Node / RDF.Uri
            The subject to delete statements about

        context : str
            (optional) Name of the context to execute the query against
        """

        subj_string = self.term_to_sparql(subject)

        query = ""

        if context is not None:
            query += "WITH <%s/%s>" % (self.endpoints['contexts'], context)

        query += """
            DELETE { %s ?p ?o}
            WHERE { ?s ?p ?o }
        """ % (subj_string)

        self.update(query)


    def term_to_sparql(self, term):
        """Convert an RDF term to a suitable string to be inserted into a
        SPARQL query.
        """

        if isinstance(term, str):
            # Do nothing to bindings
            if term.startswith('?'):
                return term
            else:
                return "'''%s'''" % term
        elif isinstance(term, RDF.Node):
            if term.is_resource():
                return '<%s>' % str(term)
            else:
                return "'''%s'''" % str(term)
        elif isinstance(term, RDF.Uri):
            return '<%s>' % str(term)


    def processJSONResponse(self, response):
        """Process a JSON response from the Repository and create a friendlier
        format. The format is a list of Dicts, where the names in each dict
        match the bindings of the query.
        """

        results = []

        if 'results' not in response or 'bindings' not in response['results']:
            return results

        variable_names = response['head']['vars']

        for binding in response['results']['bindings']:
            row = {}

            for var in variable_names:
                value_type = binding[var]['type']

                if value_type == "uri":
                    row[var] = "<%s>" % binding[var]['value']
                else:
                    row[var] = binding[var]['value']

            results.append(row)

        return results
