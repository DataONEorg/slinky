import requests

class Repository:
    def __init__(self, store, name, ns={}):
        self.store = store
        self.name = name
        self.ns = ns

        # Check if repository exists. Create if it doesn't.
        if self.exists():
            print "Successfully set up repository connection."
        else:
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
        endpoint = "/".join(["http://" + self.store.host + ":" + self.store.port, "openrdf-sesame", "repositories", self.name, "size"])
        r = requests.get(endpoint)

        if r.text.startswith("Unknown repository:"):
            return -1

        return int(r.text)

    def clear(self):
        self.delete({'s': '?s', 'p': '?p', 'o': '?o'})

    def export(self):
        endpoint = "/".join(["http://" + self.store.host + ":" + self.store.port, "openrdf-workbench", "repositories", self.name, "export"])

        headers = {
            'Accept': 'text/turtle'
        }

        r = requests.get(endpoint, params=headers)

        return r.text

    def statements(self):
        headers = { "Accept": "application/json" }
        endpoint = "/".join(["http://" + self.store.host + ":" + self.store.port, "openrdf-sesame", "repositories", self.name, "statements"])
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
        endpoint = "/".join(["http://" + self.store.host + ":" + self.store.port, "openrdf-sesame", "repositories", self.name, "namespaces"])

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
        endpoint = "/".join(["http://" + self.store.host + ":" + self.store.port, "openrdf-sesame", "repositories", self.name, "namespaces", namespace])
        r = requests.get(endpoint)

        return r.text

    def addNamespace(self, namespace, value):
        endpoint = "/".join(["http://" + self.store.host + ":" + self.store.port, "openrdf-sesame", "repositories", self.name, "namespaces", namespace])

        r = requests.put(endpoint, data = value)

    def removeNamespace(self, namespace):
        endpoint = "/".join(["http://" + self.store.host + ":" + self.store.port, "openrdf-sesame", "repositories", self.name, "namespaces", namespace])

        r = requests.delete(endpoint)

    def namespacePrefixString(self):
        ns = self.namespaces()

        ns_strings = []

        for key in ns:
            ns_strings.append("PREFIX %s:<%s>" % (key, ns[key]))

        return "\n".join(ns_strings)

    def query(self, query_string):
        headers = { "Accept": "application/json" }
        endpoint = "/".join(["http://" + self.store.host + ":" + self.store.port, "openrdf-workbench", "repositories", self.name, "query"])

        sparql_query = "".join([self.namespacePrefixString(), query_string]).strip()

        query_params = {
            'action': 'exec',
            'queryLn': 'SPARQL',
            'query': sparql_query,
            'infer': 'false'
        }

        r = requests.get(endpoint, params = query_params, headers=headers)
        response = r.json()
        results = self.processJSONResponse(response)

        return results

    def all(self):
        headers = { "Accept": "application/json" }
        endpoint = "/".join(["http://" + self.store.host + ":" + self.store.port, "openrdf-workbench", "repositories", self.name, "query"])

        sparql_query = """
        %s
        SELECT * WHERE { ?s ?p ?o }
        """ % self.namespacePrefixString()

        sparql_query = sparql_query.strip()

        query_params = {
            'action': 'exec',
            'queryLn': 'SPARQL',
            'query': sparql_query,
            'infer': 'false'
        }

        r = requests.get(endpoint, params = query_params, headers=headers)
        response = r.json()
        results = self.processJSONResponse(response)

        return results

    def find(self, triple):
        headers = { "Accept": "application/json" }
        endpoint = "/".join(["http://" + self.store.host + ":" + self.store.port, "openrdf-workbench", "repositories", self.name, "query"])

        sparql_query = """
        %s
        SELECT *
        WHERE { %s %s %s }
        """ % (self.namespacePrefixString(), triple['s'], triple['p'], triple['o'])

        sparql_query = sparql_query.strip()

        query_params = {
            'action': 'exec',
            'queryLn': 'SPARQL',
            'query': sparql_query,
            'infer': 'false'
        }

        r = requests.get(endpoint, params = query_params, headers=headers)
        response = r.json()
        results = self.processJSONResponse(response)

        return results

    def insert(self, triple):
        endpoint = "/".join(["http://" + self.store.host + ":" + self.store.port, "openrdf-workbench", "repositories", self.name, "update"])

        sparql_query = """
        %s
        INSERT DATA { %s %s %s }
        """ % (self.namespacePrefixString(), triple['s'], triple['p'], triple['o'])
        sparql_query = sparql_query.strip()

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        print sparql_query

        query_params = {
            'queryLn': 'SPARQL',
            'update': sparql_query,
        }

        r = requests.post(endpoint, headers=headers, data = query_params)

    def delete(self, triple):
        endpoint = "/".join(["http://" + self.store.host + ":" + self.store.port, "openrdf-workbench", "repositories", self.name, "update"])

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        sparql_query = """
        %s
        DELETE { ?s ?p ?o }
        WHERE { %s %s %s }
        """ % (self.namespacePrefixString(), triple['s'], triple['p'], triple['o'])

        sparql_query = sparql_query.strip()

        query_params = {
            'queryLn': 'SPARQL',
            'update': sparql_query,
        }

        r = requests.post(endpoint, headers=headers, data = query_params)

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
