import os
from urllib import parse

from starlette.applications import Starlette
from starlette.responses import Response, HTMLResponse, JSONResponse
from starlette.staticfiles import StaticFiles
from starlette.exceptions import HTTPException
from starlette.templating import Jinja2Templates
from starlette.schemas import SchemaGenerator
import httpx

from slinky.client import SlinkyClient
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

templates = Jinja2Templates(directory='templates')
app = Starlette(debug=False)
app.mount('/static', StaticFiles(directory='static'), name='static')


async def not_found(request, exc):
    return HTMLResponse("404 Not Found", status_code=exc.status_code)


async def bad_request(request, exc):
    return HTMLResponse(f"400 Bad Request {exc.detail}", status_code=exc.status_code)


async def not_supported(request, exc):
    return HTMLResponse("415 Not Supported", status_code=exc.status_code)


exception_handlers = {
    404: not_found,
    400: bad_request,
    415: not_supported
}

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
        "endpoint": os.environ.get("SLINKY_WEB_ENDPOINT", "/sparql")
    }
    return templates.TemplateResponse(template, context)


@app.route('/sparql', methods=["POST"])
async def sparql(request):
    """
    Proxy queries to a backend SPARQL endpoint

    TODO: This function is not nearly done. The basic idea here is that this
    app responds on /sparql and proxies incoming requests to Virutoso's
    SPARQL endpoint. Things are hard-coded right now but this handler could
    get modified to actually parse and forward the incoming query and any
    relevant headers as well dynamically format the response also based on those
    headers. See TODOs below.
    """
    # TODO: Set up and re-use a client across requests. Consider a Pool or
    #       whatever makes sense.
    # TODO: Set headers, esp. user-agent
    client = httpx.Client(
        base_url=os.environ.get(
            "VIRTUOSO_URL", "http://localhost:8890"),
        headers={

        })

    print(f"Client base url is {client.base_url}")

    # Pull out incoming query from the request
    form_data = await request.form()

    if "query" not in form_data:
        raise HTTPException(400, detail="Missing 'query' form parameter")

    query = form_data["query"]

    # Set up proxied request
    # TODO: Forward headers from request instead of hard-coding
    request_headers = {
        "accept": "application/sparql-results+json",
    }
    request_data = {
        "query": query
    }

    response = client.post(
        "/sparql", data=request_data, headers=request_headers
    )

    response.raise_for_status()

    # Return response back to client
    # TODO: Let client pick response content-type
    response_headers = {
        "content-type": "application/sparql-results+json"
    }
    # TODO: Dynamically generate response rather than assuming JSON
    return JSONResponse(response.json(), headers=response_headers)
