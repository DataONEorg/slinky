# Slinky, the DataONE Graph Store

## Overview
Service for the DataONE Linked Open Data graph.

This repository contains a deployable service that continuously updates the [DataOne](https://www.dataone.org/) [Linked Open Data](http://linkeddata.org/) graph. It was originally developed as a provider of data for the [GeoLink](http://www.geolink.org/) project, but now is a core component of the DataONE services. The service uses [Docker Compose](https://docs.docker.com/compose/) to manage a set of [Docker](https://www.docker.com/) containers that run the service. The service is intended to be deployed to a virtual machine and run with [Docker Compose](https://docs.docker.com/compose/).

The main infrastructure of the service is composed of four [Docker Compose](https://docs.docker.com/compose/) services:

1. `web`: An [Apache httpd](https://httpd.apache.org/) front-end serving static files and also reverse-proxying to an [Apache Tomcat](http://tomcat.apache.org/) server running a [GraphDB](http://graphdb.ontotext.com/display/GraphDB6/Home) Lite instance which is bundled with [OpenRDF Sesame](http://rdf4j.org) Workbench.
2. `scheduler`: An [APSchduler](https://apscheduler.readthedocs.org) process that schedules jobs (e.g., update graph with new datasets) on the `worker` at specified intervals
3. `worker`: An [RQ](http://python-rq.org/) worker process to run scheduled jobs
4. `redis`: A [Redis](http://redis.io) instance to act as a persistent store for the `worker` and for saving application state

In addition to the core infrastructure services (above), a set of monitoring/logging services are spun up by default. As of writing, these are mostly being used for development and testing but they may be useful in production:

1. `elasticsearch`: An [ElasticSearch](https://www.elastic.co/products/elasticsearch) instance to store, index, and support analysis of logs
2. `logstash`: A [Logstash](https://www.elastic.co/products/logstash) instance to facilitate the log pipeline
3. `kibana`: A [Kibana](https://www.elastic.co/products/kibana) instance to search and vizualize logs
4. `logspout`: A [Logspout](https://github.com/gliderlabs/logspout) instance to collect logs from the [Docker](https://www.docker.com/) containers
5. `cadvisor`: A [cAdvisor](https://github.com/google/cadvisor) instance to monitor resource usage on each [Docker](https://www.docker.com/) container
6. `rqdashboard`: An [RQ Dashboard](https://github.com/nvie/rq-dashboard) instance to monitor jobs.

As the service runs, the graph store will be continuously updated as datasets are added/updated on [DataOne](https://www.dataone.org/). Another scheduled job exports the statements in the graph store and produces a Turtle dump of all statements at [http://dataone.org/d1lod.ttl](http://dataone.org/d1lod.ttl).

### Contents of This Repository

```
.
├── d1lod       # Python package which supports other services
├── docs        # Detailed documentation beyond this file
├── logspout    # Custom Dockerfile for logspout
├── logstash    # Custom Dockerfile for logstash
├── redis       # Custom Dockerfile for Redis
├── rqdashboard # Custom Dockerfile for RQ Dashboard
├── scheduler   # Custom Dockerfile for APScheduler process
├── web         # Apache httpd + Tomcat w/ GraphDB
├── worker      # Custom Dockerfile for RQWorker process
└── www         # Local volume holding static files
```

Note: In order to run the service without modification, you will need to create a 'webapps' directory in the root of this repository containing 'openrdf-workbench.war' and 'openrdf-sesame.war':

```
.
├── webapps
│   ├── openrdf-sesame.war
└   └── openrdf-workbench.war
```

These aren't included in the repository because we're using GraphDB Lite which doesn't have a public download URL. These WAR files can just be the base Sesame WAR files which support a variety of backend graph stores but code near https://github.com/ec-geolink/d1lod/blob/master/d1lod/d1lod/sesame/store.py#L90 will need to be modified correspondingly.


## What's in the graph?

For an overview of what concepts the graph contains, see the [mappings](/docs/mappings.md) documentation.


## Getting up and running

Assuming you are set up to to use [Docker](https://www.docker.com/) (see the [User Guide](https://docs.docker.com/engine/userguide/) to get set up):

```
git clone https://github.com/DataONEorg/slinky
cd slinky
# Create a webapps folder with openrdf-sesame.war and openrdf-workbench.war (See above note)
docker-compose up # May take a while
```

After running the above `docker-compose` command, the above services should be started and available (if appropriate) on their respective ports:
1. Apache httdp → $DOCKER_HOST:80`
2. OpenRDF Workbench → `$DOCKER_HOST:8080/openrdf-workbench/`
3. Kibana (logs) → `$DOCKER_HOST:5601`
4. cAdvisor → `$DOCKER_HOST:8888`

Where `$DOCKER_HOST` is `localhost` if you're running [Docker](https://www.docker.com/) natively or some IP address if you're running [Docker Machine](https://docs.docker.com/machine/). Consult the [Docker Machine](https://docs.docker.com/machine/) documentation to find this IP address. When deployed on a Linux machine, [Docker](https://www.docker.com/) is able to bind to localhost under the default configuration.


## Testing

Tests are written using [PyTest](http://pytest.org/latest/). Install [PyTest](http://pytest.org/latest/) with

```
pip install pytest
cd d1lod
py.test
```

As of writing, only tests for the supporting Python package (in directory './d1lod') have been written.
Note: The test suite assumes you have a running instance of [OpenRDF Sesame](http://rdf4j.org) running on http://localhost:8080 which means the Workbench is located at http://localhost:8080/openrdf-workbench and the Sesame interface is available at http://localhost:8080/openrdf-sesame.
