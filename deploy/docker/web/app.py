from starlette.applications import Starlette
from starlette.responses import Response, HTMLResponse, PlainTextResponse
from starlette.routing import Route
from starlette.exceptions import HTTPException
from xml.etree import ElementTree as XML
from urllib import parse
import RDF
import httpx
from werkzeug import http
from d1lod.client import SlinkyClient

serializer_map = {
    "text/turtle": "turtle",
    "text/ntriples": "ntriples",
    "application/rdf+xml": "rdfxml",
    "*/*": "turtle",
}


async def not_found(request, exc):
    return HTMLResponse("404 Not Found", status_code=exc.status_code)


async def not_supported(request, exc):
    return HTMLResponse("415 Not Supported", status_code=exc.status_code)


exception_handlers = {404: not_found, 415: not_supported}

client = SlinkyClient()


class SlinkyWebClient:
    async def get_serializer_name(self, accept):
        parsed = http.parse_accept_header(accept)

        # Find first
        for element in parsed:
            if element[0] in serializer_map:
                return serializer_map[element[0]]

        raise HTTPException(415, detail="Not Supported")

    async def process(self, id, accept="text/turtle"):
        serializer_name = await self.get_serializer_name(accept)
        model = client.get_model_for_dataset(id)
        serializer = RDF.Serializer(serializer_name)

        return serializer.serialize_model_to_string(model)


web_client = SlinkyWebClient()


async def index(request):
    return PlainTextResponse("Slinky")


async def get(request):
    id = request.query_params["id"]
    result = await web_client.process(parse.unquote_plus(id), request.headers["accept"])

    return Response(result, media_type="text/turtle")


routes = [Route("/", index), Route("/get", get)]


app = Starlette(debug=False, routes=routes)
