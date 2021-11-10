# Slinky, the DataONE Graph Store

## Overview

Service for the DataONE Linked Open Data graph.

This repository contains the deployment and code that makes up the
DataONE graph store.

The main infrastructure of the service is composed of four services and is essentially a backround job system ([RQ](https://python-rq.org/)) hooked into an RDF triplestore ([Virtuoso](http://vos.openlinksw.com/owiki/wiki/VOS)) for persistence:

1. `virtuoso`: Acts as the backend graph store
2. `scheduler`: An [APSchduler](https://apscheduler.readthedocs.org) process that schedules jobs (e.g., update graph with new datasets) on the `worker` at specified intervals
3. `worker`: An [RQ](http://python-rq.org/) worker process to run scheduled jobs
4. `redis`: A [Redis](http://redis.io) instance to act as a persistent store for the `worker` and for saving application state

![slinky architecture diagram showing the components in the list above connected with arrows](./docs/slinky-architecture.png)

As the service runs, the graph store will be continuously updated as datasets are added/updated on [DataOne](https://www.dataone.org/). Another scheduled job exports the statements in the graph store and produces a Turtle dump of all statements at [http://dataone.org/d1lod.ttl](http://dataone.org/d1lod.ttl).

### Contents of This Repository

```
.
├── d1lod       # The code that handles the graph updates
├── deploy      # The Kubernetes deployment files
├── docs         # Detailed documentation beyond this file
```

## What's in the graph?

For an overview of what concepts the graph contains, see the [mappings](/docs/mappings.md) documentation.

## Deployment

The deployment consists of a handful of deployment files and a few
associated services. To bring the deployments and services online, use
`kubectl -f <deployment_file>` on each file in the `deploy/deployment/`
and `deploy/service/` directories. It's recommended to start the redis
and virtuoso images _before_ the workers and scheduler.



### Scaling Pods

The pods should be scaled with `kubectl scale`, shown below.

```
kubectl scale --replicas=0 deployments/{pod-name}
```


### Protecting the Virtuoso SPARQLEndpoint

We don't want open access to the `sparql/` endpoint that Virtuoso
exposes. To protect the endpoint, follow
[this](http://vos.openlinksw.com/owiki/wiki/VOS/VirtSPARQLProtectSQLDigestAuthentication)
guide from Open Link. While performing 'Step 6', use the `Browse` button
to locate the authentication function rather than copy+pasting
`DB.DBA.HP_AUTH_SQL_USER;`, which is suggested by the guide.

## Testing

Tests are written using [PyTest](http://pytest.org/latest/). Install [PyTest](http://pytest.org/latest/) with

```
pip install pytest
cd d1lod
py.test
```

As of writing, only tests for the supporting Python package (in directory './d1lod') have been written.
Note: The test suite assumes you have a running instance of [OpenRDF Sesame](http://rdf4j.org) running on http://localhost:8080 which means the Workbench is located at http://localhost:8080/openrdf-workbench and the Sesame interface is available at http://localhost:8080/openrdf-sesame.
