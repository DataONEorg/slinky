import sys
import os
import tempfile
import re

import httpx
import logging
import RDF

from ..version import __version__

logger = logging.getLogger(__name__)

DELETE_RESPONSE_PATTERN = r"Delete from <.+>, (\d+) \(or less\) triples -- done"


class VirtuosoStore:
    def __init__(
        self,
        endpoint="http://localhost:8890",
        default_graph="https://dataone.org",
    ):
        self.endpoint = endpoint
        self.graph = default_graph
        self.client = None

        self.setup_client()

    def __del__(self):
        if self.client is not None:
            logger.debug("Closing httpx.Client on SparqlTripleStore")
            self.client.close()

    def get_ua_string(self):
        return "Slinky/{} httpx/{} Python/{}".format(
            __version__, httpx.__version__, "{}.{}.{}".format(*sys.version_info)
        )

    def setup_client(self):
        headers = {"user-agent": self.get_ua_string()}

        self.client = httpx.Client(base_url=self.endpoint, headers=headers)

    def query(self, query_text, parse_into_model=False):
        headers = {
            "accept": "application/sparql-results+json",
        }
        data = {"query": query_text}

        response = self.client.post(
            f"{self.endpoint}/sparql", data=data, headers=headers
        )
        response.raise_for_status()

        if parse_into_model:
            return self.parse_response_as_model(response)
        else:
            return self.parse_response(response)

    def all(self, limit=100):
        query_text = f"""SELECT ?s ?p ?o
        FROM <{self.graph}>
        WHERE {{ ?s ?p ?o . }}
        LIMIT {limit}"""

        return self.query(query_text, parse_into_model=True)

    def count(self, pattern="?s ?p ?o"):
        query_text = f"""SELECT count(*)
        FROM <{self.graph}>
        WHERE {{ {pattern} }}"""

        response = self.query(query_text, parse_into_model=False)

        return int(str(response[0]["callret-0"]))

    def delete(self, pattern):
        query_text = f"""WITH <{self.graph}>
        DELETE {{ {pattern } }}
        WHERE {{ {pattern} }}"""

        response = self.query(query_text, parse_into_model=False)

        return self.parse_delete_response(str(response[0]["callret-0"]))

    def clear(self):
        query_text = f"""CLEAR GRAPH <{self.graph}>"""

        response = self.query(query_text, parse_into_model=False)

        if str(response[0]["callret-0"]) != f"Clear graph <{self.graph}> -- done":
            raise Exception

        return True

    def insert_statement(self, statement):
        storage = RDF.MemoryStorage()
        model = RDF.Model(storage=storage)
        model.append(statement)

        return self.insert_model(model)

    def insert_model(self, model):
        serializer = RDF.NTriplesSerializer()

        # Return value since Virtuoso's response isn't interesting or useful
        status = False

        with tempfile.NamedTemporaryFile(mode="r+b") as tf:
            serializer.serialize_model_to_file(tf.name, model)

            headers = {
                "Expect": "100-Continue",
                "Content-Length": str(os.path.getsize(tf.name)),
            }

            response = self.client.post(
                f"{self.endpoint}/sparql-graph-crud?graph-uri={self.graph}",
                content=tf,
                headers=headers,
            )
            response.raise_for_status()

            status = True

        return status

    def parse_response_as_model(self, response):
        storage = RDF.MemoryStorage()
        model = RDF.Model(storage=storage)

        resp_json = response.json()
        bindings = resp_json["results"]["bindings"]

        for binding in bindings:
            statement = RDF.Statement(
                subject=self.parse_node(binding["s"]),
                predicate=self.parse_node(binding["p"]),
                object=self.parse_node(binding["o"]),
            )

            model.add_statement(statement)

        return model

    def parse_response(self, response):
        """Parse response into a list of dicts"""
        resp_json = response.json()

        bindings = resp_json["results"]["bindings"]

        return [self.parse_binding(item) for item in bindings]

    def parse_binding(self, binding):
        parsed = {}

        for var in binding:
            parsed[var] = self.parse_node(binding[var])

        return parsed

    def parse_node(self, node):
        if node["type"] == "literal":
            return RDF.Node(literal=node["value"])
        elif node["type"] == "typed-literal":
            return RDF.Node(literal=node["value"], datatype=RDF.Uri(node["datatype"]))
        elif node["type"] == "uri":
            return RDF.Node(RDF.Uri(node["value"]))
        else:
            raise Exception(f"Unsupported node type: {node}")

    def parse_delete_response(self, response):
        return int(re.findall(DELETE_RESPONSE_PATTERN, response)[0])
