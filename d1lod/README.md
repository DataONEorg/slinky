# D1 LOD Python Package

This directory contains the Python package that supports the LOD service.

## Contents

- d1lod.jobs: Jobs for the D1 LOD Service
- d1lod.util: Helper methods
- d1lod.metadata.*: Methods for extracting information from Science Metadata
- d1lod.people.*: Methods for extracting information about people and organizations from Science Metadata
- d1lod.sesame.*: A light-weight wrapper around the Sesame Workbench and its REST API

## Testing

### Pre-requisites:

- Sesame w/ GraphDB must be running on 'http://localhost:8000/openrdf-workbench'

### Running

From this directory, run:

`py.test`
