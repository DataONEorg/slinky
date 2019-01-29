# D1 LOD Python Package

This directory contains the Python package that supports the LOD service.

## Contents

- d1lod.jobs: Jobs for the D1 LOD Service
- d1lod.util: Helper methods
- d1lod.metadata.*: Methods for extracting information from Science Metadata
- d1lod.people.*: Methods for extracting information about people and organizations from Science Metadata
- d1lod.virtuoso.*: A light-weight wrapper around the Virtuoso store and its HTTP API

## Testing

### Pre-requisites:

- Virtuoso Store must be running on 'http://localhost:8000/virtuoso/conductor'

### Running

From this directory, run:

`py.test`
