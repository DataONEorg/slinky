from starlette.applications import Starlette
from starlette.responses import Response, HTMLResponse, PlainTextResponse
from starlette.routing import Route
from starlette.exceptions import HTTPException
from xml.etree import ElementTree as XML
from urllib import parse
import RDF
import httpx
from werkzeug import http


serializer_map = {
    'text/turtle': 'turtle',
    'text/ntriples': 'ntriples',
    'application/rdf+xml': 'rdfxml',
    '*/*': 'turtle',
}

async def not_found(request, exc):
    return HTMLResponse("404 Not Found", status_code=exc.status_code)


async def not_supported(request, exc):
    return HTMLResponse("415 Not Supported", status_code=exc.status_code)


exception_handlers = {
    404: not_found,
    415: not_supported
}

class D1GraphClient:
    async def get_serializer_name(self, accept):
        parsed = http.parse_accept_header(accept)

        # Find first
        for element in parsed:
            if element[0] in serializer_map:
                return serializer_map[element[0]]

        raise HTTPException(415, detail="Not Supported")

    async def process(self, id, accept="text/turtle"):
        serializer_name = await self.get_serializer_name(accept)

        # Setup
        storage = RDF.MemoryStorage()
        model = RDF.Model(storage)

        # Fetch document
        async with httpx.AsyncClient() as client:
            r = await client.get("https://arcticdata.io/metacat/d1/mn/v2/object/{}".format(parse.quote_plus(id)))

        r.raise_for_status()

        # Parse document
        doc = XML.fromstring(r.text)

        # Set aside a common dataset Node
        dataset = RDF.Node(RDF.Uri("https://dataone.org/datasets/{}".format(parse.quote_plus(id))))

        # rdf:type
        sttm = RDF.Statement(
            dataset,
            RDF.Node(RDF.Uri("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")),
            RDF.Node(RDF.Uri("https://schema.org/Dataset"))
        )
        model.add_statement(sttm)

        # title -> schema:name
        titles = doc.findall(".//dataset/title")

        for title in titles:
            sttm = RDF.Statement(
                dataset,
                RDF.Node(RDF.Uri("https://schema.org/name")),
                RDF.Node(literal = title.text)
            )

            model.add_statement(sttm)

        # Serialize
        serializer = RDF.Serializer(serializer_name)

        return serializer.serialize_model_to_string(model)


client = D1GraphClient()


async def index(request):
    return PlainTextResponse("/")


async def generate(request):
    id = request.query_params['id']
    result = await client.process(parse.unquote_plus(id), request.headers['accept'])

    return Response(result, media_type = "text/turtle")


routes = [
    Route("/", index),
    Route("/generate", generate)
]


app = Starlette(debug=False, routes=routes)
