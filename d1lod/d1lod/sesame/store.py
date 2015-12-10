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
        endpoint = self.endpoints['protocol']

        r = requests.get(endpoint)

        return r.text

    def repositories(self):
        # headers = { "Accept": "application/rdf+xml" }
        headers = { "Accept": "application/json" }

        endpoint = self.endpoints['repositories']

        r = requests.get(endpoint, headers=headers)

        if r.status_code != 200:
            print "Failed to get listing of repositories."
            return []

        response = r.json()

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
        """Determines whether a repository with the given name exists in the Store."""

        if name is None:
            return False

        repos = self.repositories()

        if name in repos:
            return True
        else:
            return False

    def createRepository(self, name):

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

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

        r = requests.post(endpoint, headers = headers, data = data)

    def deleteRepository(self, name):
        endpoint = self.endpoints['deleteRepository'] + '/' + name + "/delete"

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        data = {
            'id': name
        }

        r = requests.post(endpoint, headers = headers, data = data)
