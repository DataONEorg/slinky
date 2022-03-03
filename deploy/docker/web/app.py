import os
from urllib import parse

from starlette.applications import Starlette
from starlette.responses import Response, HTMLResponse, PlainTextResponse, RedirectResponse
from starlette.staticfiles import StaticFiles
from starlette.exceptions import HTTPException
from starlette.templating import Jinja2Templates
from starlette.schemas import SchemaGenerator


from d1lod.client import SlinkyClient
import RDF
import requests
from werkzeug import http

serializer_map = {
    "text/turtle": "turtle",
    "text/ntriples": "ntriples",
    "application/rdf+xml": "rdfxml",
    "*/*": "turtle",
}

schemas = SchemaGenerator(
    {
        "openapi": "3.0.0", "info": {
        "title": "Slinky API", "version": "1.0"
    }
    }
)

deployment_base = os.getenv('DEPLOYMENT_BASE', 'https://api.test.dataone.org')
ENDPOINT= '/virtuoso/sparql'
templates = Jinja2Templates(directory='templates')
app = Starlette(debug=False)
app.mount('/static', StaticFiles(directory='static'), name='static')


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


@app.route('/get')
async def get(request):
    id = request.query_params["id"]
    result = await web_client.process(parse.unquote_plus(id), request.headers["accept"])

    return Response(result, media_type="text/turtle")


@app.route('/')
async def homepage(request):
    template = "index.html"
    context = {
        "request": request,
        "endpoint": "https://api.test.dataone.org/slinky/virtuoso/sparql",
        "deployment_base": deployment_base
    }
    return templates.TemplateResponse(template, context)
