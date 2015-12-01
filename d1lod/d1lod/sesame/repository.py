"""A Repository is a light-weight wrapper around a Sesame Repository API:

    http://rdf4j.org/sesame/2.7/docs/system.docbook?view#The_Sesame_Server_REST_API
    http://docs.s4.ontotext.com/display/S4docs/Fully+Managed+Database#FullyManagedDatabase-cURL%28dataupload%29
"""

import requests

class Repository:
    def __init__(self, store, name, ns={}):
        self.store = store
        self.name = name
        self.ns = ns
        self.endpoints = {
            'size':         'http://%s:%s/openrdf-sesame/repositories/%s/size' % (self.store.host, self.store.port, self.name),
            'statements':   'http://%s:%s/openrdf-sesame/repositories/%s/statements' % (self.store.host, self.store.port, self.name),
            'namespaces':   'http://%s:%s/openrdf-sesame/repositories/%s/namespaces' % (self.store.host, self.store.port, self.name),
            'query':        'http://%s:%s/openrdf-sesame/repositories/%s' % (self.store.host, self.store.port, self.name),
            'contexts':   'http://%s:%s/openrdf-sesame/repositories/%s/rdf-graphs' % (self.store.host, self.store.port, self.name)

        }

        # Check if repository exists. Create if it doesn't.
        if not self.exists():
            print "Creating repository '%s'." % name
            self.store.createRepository(name)

        existing_namespaces = self.namespaces()

        for prefix in ns:
            if prefix in existing_namespaces:
                continue

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
        endpoint = self.endpoints['size']
        r = requests.get(endpoint)

        if r.text.startswith("Unknown repository:"):
            return -1

        return int(r.text)

    def clear(self):
        response = None

        try:
            response = requests.delete(self.endpoints['statements'])
        except:
            print "Failed to clear repository."


        if response is None or response.status_code >= 300:
            print "Something went wrong when deleting all statements from the repository."
            print response.text

    def import_from_text(self, text, context=None, format='turtle'):
        """Import text containing RDF into the repository."""

        if format != 'turtle':
            print "Format of %s is not yet implemented. Doing nothing." % format
            return

        if context is None:
            endpoint = self.endpoints['statements']
        else:
            endpoint = self.endpoints['contexts'] + '/' + context

        headers = {
            'Content-Type': 'text/turtle',
            'charset': 'UTF-8'
        }

        r = requests.put(endpoint, headers=headers, data=text)


    def import_from_file(self, filename, context=None, format='turtle'):
        """Import a file containing RDF into the repository."""

        if format != 'turtle':
            print "Format of %s is not yet implemented. Doing nothing." % format
            return

        if context is None:
            endpoint = self.endpoints['statements']
        else:
            endpoint = self.endpoints['contexts'] + '/' + context

        headers = {
            'Content-Type': 'text/turtle',
            'charset': 'UTF-8'
        }

        files = {
            'file': open(filename, 'rb')
        }

        r = requests.post(endpoint, headers=headers, files=files)


    def export(self, format='turtle'):
        """Export RDF from the repository in the specified format."""

        if format != 'turtle':
            print "Format of %s is not yet implemented. Doing nothing." % format
            return

        endpoint = "/".join(["http://" + self.store.host + ":" + self.store.port, "openrdf-workbench", "repositories", self.name, "export"])

        headers = {
            'Accept': 'text/turtle'
        }

        r = requests.get(endpoint, params=headers)

        return r.text

    def statements(self):
        headers = { "Accept": "application/json" }
        endpoint = self.endpoints['statements']

        query_params = {
            'infer': 'false'
        }

        r = requests.get(endpoint, params = query_params)

        return r.text

    def namespaces(self):
        """
        Return the namespaces for the repository as a Dict.
        """

        headers = { "Accept": "application/json" }
        endpoint = self.endpoints['namespaces']

        r = requests.get(endpoint, headers=headers)

        if r.text.startswith("Unknown repository:"):
            return {}

        response =  r.json()
        bindings = response['results']['bindings']

        namespaces = {}

        for binding in bindings:
            prefix = binding['prefix']['value']
            namespace = binding['namespace']['value']

            namespaces[prefix] = namespace

        return namespaces

    def getNamespace(self, namespace):
        ns = self.namespaces()

        if namespace in ns:
            return ns[namespace]
        else:
            return None

    def addNamespace(self, namespace, value):
        endpoint = self.endpoints['namespaces'] + '/' + namespace

        r = requests.put(endpoint, data = value)

        if r.status_code != 204:
            print "Adding namespace failed."
            print "Status Code: %d." % r.status_code
            print r.text

    def removeNamespace(self, namespace):
        endpoint = self.endpoints['namespaces']

        requests.delete(endpoint)

    def namespacePrefixString(self):
        ns = self.namespaces()

        ns_strings = []

        for key in ns:
            ns_strings.append("PREFIX %s:<%s>" % (key, ns[key]))

        return "\n".join(ns_strings)

    def query(self, query_string, format='application/json'):
        headers = { 'Accept': format }
        endpoint = self.endpoints['query']
        params = {
            'queryLn': 'SPARQL',
            'query': self.namespacePrefixString() + query_string.strip(),
            'infer': 'false'
        }

        r = requests.get(endpoint, headers=headers, params=params)

        if r.status_code != 200:
            print "SPARQL QUERY failed. Status was not 200 as expected."
            print r.status_code
            print r.text

        response_json = r.json()
        results = self.processJSONResponse(response_json)

        return results


    def update(self, query_string):
        headers = {}
        endpoint = self.endpoints['update']

        r = requests.post(endpoint, headers=headers, data={ 'update': query_string.strip() })

        if r.status_code != 204:
            print "SPARQL UPDATE failed. Status was not 204 as expected."
            print r.text

    def statements(self, format='text/turtle'):
        headers = { 'Accept': format }
        endpoint = self.endpoints['statements']
        params = {
            'infer': 'false'
        }

        r = requests.get(endpoint, headers=headers, params=params)

        if r.status_code != 200:
            print "GET Statements failed. Status code was not 200 as expected."
            print r.status_code
            print r.text

        return r.text

    def contexts(self):
        """Get a list of contexts in the repository."""

        endpoint = self.endpoints['contexts']

        headers = { "Accept": "application/json" }

        r = requests.get(endpoint, headers=headers)

        return self.processJSONResponse(r.json())

    def processJSONResponse(self, response):
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
