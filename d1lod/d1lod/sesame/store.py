"""d1lod.sesame.store

A wrapper around a Sesame Server. Used mainly to perform three tasks:

    1. Get a list of the repositories
    2. Create repositories
    3. Delete repositories
    

Reference material:

http://rdf4j.org/sesame/2.7/docs/system.docbook?view#The_Sesame_Server_REST_API
http://docs.s4.ontotext.com/display/S4docs/Fully+Managed+Database#FullyManagedDatabase-cURL%28dataupload%29
"""

import requests


class Store:
    def __init__(self, host="localhost", port=8080):
        self.host = host
        self.port = str(port)

        self.endpoints = {
            'protocol': 'http://%s:%s/openrdf-sesame/protocol' % (self.host, self.port),
            'repositories': 'http://%s:%s/openrdf-sesame/repositories' % (self.host, self.port),
            'createRepository': 'http://%s:%s/openrdf-workbench/repositories/NONE/create' % (self.host, self.port),
            'deleteRepository': 'http://%s:%s/openrdf-workbench/repositories' % (self.host, self.port)
        }


    def __str__(self):
        return """%s:%s""" % (self.host, self.port)


    def protocol(self):
        """Returns the protocol version for the Sesame interface."""

        endpoint = self.endpoints['protocol']

        r = requests.get(endpoint)

        if r.status_code != 200:
            print "Failed to get protocol %s." % name
            print r.text

        return r.text


    def repositories(self):
        headers = { "Accept": "application/json" }
        endpoint = self.endpoints['repositories']

        r = requests.get(endpoint, headers=headers)

        if r.status_code != 200:
            print "Failed to get listing of repositories."
            return []

        try:
            response = r.json()
        except:
            print "Failed to convert response to JSON."
            print r.status_code
            print r.text
            return []

        if response is None:
            return []

        if 'results' not in response or 'bindings' not in response['results']:
            return []

        bindings = response['results']['bindings']

        if len(bindings) < 1:
            return []

        repo_ids = [b['id']['value'] for b in bindings]

        return repo_ids


    def hasRepository(self, name):
        """Determines whether a repository with the given name exists in the
        Store.
        """

        if name is None:
            return False

        repos = self.repositories()

        if name in repos:
            return True
        else:
            return False

    def createRepository(self, name):
        """Create a repository with the given name."""

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        endpoint = self.endpoints['createRepository']

        # Defaults for OWLIM-Lite
        data = {
            'type': 'owlim-lite',
            'Repository ID': name,
            'Repository title': name,
            'Storages': 'storage',
            'Rule-set': 'owl-horst-optimized',
            'Base URL': 'http://example.org/owlim',
            'Entity index size': '200000',
            'No Persistence': 'false',
            'Imported RDF files': '',
            "Default namespaces for imports(';' delimited)": '',
            'Job size': '1000',
            'New triples file': ''
        }

        # Returns 200 status and a SPARQL result of the new state
        r = requests.post(endpoint, headers=headers, data=data)

        if r.status_code != 200:
            print "Failed to create repository %s." % name
            print r.text


    def deleteRepository(self, name):
        """Deletes the repository with the given name."""

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        endpoint = self.endpoints['deleteRepository'] + '/' + name + "/delete"

        data = {
            'id': name
        }

        # Returns 200 status and a SPARQL result of the new state
        r = requests.post(endpoint, headers=headers, data=data)

        if r.status_code != 200:
            print "Failed to delete repository %s." % name
            print r.text
