# d1lod

This directory contains the Python package that supports the Slinky.

## Contents

- d1lod.jobs: Jobs for the D1 LOD Service
- d1lod.util: Helper methods
- d1lod.metadata.*: Methods for extracting information from Science Metadata
- d1lod.people.*: Methods for extracting information about people and organizations from Science Metadata
- d1lod.graph: A light-weight wrapper around the Virtuoso store and its HTTP API for interacting with graphs
- d1lod.interface: A light-weight wrapper around the Virtuoso store and its HTTP API 

## Setup

This package is a bit harder to set up than normal Python projects because it uses the [librdf](https://librdf.org/bindings/) (Redland) Python bindings which aren't on PyPi.
You should install the Redland Python bindings as appropriate on your system.
Under macOS, see [our guide](./docs/install-redlands-bindings.md).

The rest of this package's dependencies can be installed with the usual `pip install -r requirements.txt`.

## Testing

### Pre-requisites

The test suite is mostly made of integration tests that depend on being able to access an RDF triplestore while the test suite runs.
We've developed and tested with [Virtuoso Open Source](http://vos.openlinksw.com/owiki/wiki/VOS) and other RDF triplestore may require modifications to work correctly.

The pre-requisities for running the test suite are:

1. Virtuoso or a similar RDF triplestore
2. pytest

A quick way to get Virtuoso running is via [Docker](https://www.docker.com):

```
docker run -it -e "SPARQL_UPDATE=true" -p 8890:8890 tenforce/virtuoso
```

### Running

```
pytest
```
