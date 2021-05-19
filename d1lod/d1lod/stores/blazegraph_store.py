import sys
import httpx
import logging
import RDF
from urllib.parse import quote_plus as q
import xml.etree.ElementTree as ET

from ..version import __version__

logger = logging.getLogger(__name__)


class BlazegraphStore:
    def __init__(self, base_url="http://localhost:8080/bigdata", namespace="dataone"):
        self.base_url = base_url
        self.namespace = namespace

        self.endpoint = {
            "sparql": f"{self.base_url}/namespace/{self.namespace}/sparql",
            "namespace": f"{self.base_url}/namespace",
        }

        self.client = self.setup_client()
        self.ensure_namespace()

    def __del__(self):
        if self.client is not None:
            logger.debug("Closing httpx.Client on BlazegraphStore")
            self.client.close()

    def get_ua_string(self):
        return "Slinky/{} httpx/{} Python/{}".format(
            __version__, httpx.__version__, "{}.{}.{}".format(*sys.version_info)
        )

    def setup_client(self):
        headers = {
            "user-agent": self.get_ua_string(),
            "accept": "application/sparql-results+json",
        }

        return httpx.Client(base_url=self.base_url, headers=headers)

    def query(self, query_text, parse_into_model=False):
        data = {"query": query_text}

        response = self.client.post(self.endpoint["sparql"], data=data)
        response.raise_for_status()

        if parse_into_model:
            return self.parse_response_as_model(response)
        else:
            return self.parse_response(response)

    def insert(self, content, content_type="application/x-turtle"):
        headers = {
            "content-type": content_type,
        }

        response = self.client.post(
            self.endpoint["sparql"], content=content, headers=headers
        )
        response.raise_for_status()

        return self.parse_mutation_result(response.content)

    def ensure_namespace(self):
        properties = f"com.bigdata.rdf.sail.namespace={self.namespace}"
        headers = {"content-type": "text/plain"}

        response = self.client.post(
            self.endpoint["namespace"], data=properties, headers=headers
        )

        if response.status_code == 200 or response.status_code == 409:
            return response

        response.raise_for_status()

        return response

    def insert_model(self, model):
        serializer = RDF.TurtleSerializer()
        turtle = serializer.serialize_model_to_string(model)

        return self.insert(turtle)

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
            return RDF.Node(node["value"])
        elif node["type"] == "uri":
            return RDF.Node(RDF.Uri(node["value"]))
        elif node["type"] == "bnode":
            return RDF.Node(blank=node["value"])
        else:
            node_type = node["type"]
            raise Exception(
                f"Unsupported node type in parse_node of {node} with type {node_type}"
            )

    def parse_mutation_result(self, text):
        doc = ET.fromstring(text)

        return {
            "modified": int(doc.attrib["modified"]),
            "milliseconds": int(doc.attrib["milliseconds"]),
        }
