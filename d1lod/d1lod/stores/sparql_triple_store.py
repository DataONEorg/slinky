import sys
import httpx
import logging
import RDF

from ..version import __version__

logger = logging.getLogger(__name__)


class SparqlTripleStore:
    def __init__(
        self,
        endpoint="http://localhost:8890/sparql",
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
        # TODO: Set up common headers
        # User agent
        # Content-Type?
        # Accept?
        # Accept-Encoding: gzip, deflate, br
        headers = {
            "user-agent": self.get_ua_string(),
            "accept": "application/sparql-results+json",
        }

        self.client = httpx.Client(base_url=self.endpoint, headers=headers)

    # TODO: Handle VOS defined http statuses? 200, 400, 500
    # http://vos.openlinksw.com/owiki/wiki/VOS/VOSSparqlProtocol#HTTP%20Response%20Codes

    def query(self, query_text, parse_into_model=False):
        data = {"query": query_text}

        response = self.client.post(self.endpoint, data=data)
        response.raise_for_status()

        if parse_into_model:
            return self.parse_response_as_model(response)
        else:
            return self.parse_response(response)

    def all(self):
        query_text = """select ?s ?p ?o
        FROM <{}>
        WHERE {{ ?s ?p ?o . }}""".format(
            self.graph
        )

        return self.query(query_text, parse_into_model=True)

    def insert_statement(self, statement):
        query_text = """INSERT {{
            GRAPH <{}>
            {{
                {}
            }}
        }}""".format(
            self.graph, str(statement)
        )

        return self.query(query_text)

    def insert_model(self, model):
        triples = " .\n".join([str(statement) for statement in model])

        query_text = """INSERT DATA {{
            GRAPH <{}>
            {{
                {}
            }}
        }}""".format(
            self.graph, triples
        )

        return self.query(query_text)

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
        else:
            raise Exception("Unsupported")
