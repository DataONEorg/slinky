# D1LOD

## Overview
Service for the DataONE Linked Open Data graph.

This repository contains a deployable service that continuously updates the [DataOne](https://www.dataone.org/) [Linked Open Data](http://linkeddata.org/) graph for its part as a provider of data for the [GeoLink](http://www.geolink.org/) project.
The service uses [Docker Compose](https://docs.docker.com/compose/) to manage a set of [Docker](https://www.docker.com/) images that run the service. The service is intended to be deployed to a virtual machine and run with [Docker Compose](https://docs.docker.com/compose/).

The main infrastructure of the service is composed of four [Docker Compose](https://docs.docker.com/compose/) services:

1. `graphdb`: A [GraphDB](http://graphdb.ontotext.com/display/GraphDB6/Home) Lite instance (served via [Apache Tomcat](http://tomcat.apache.org/)) acting as a triple store
2. `scheduler`: An [APSchduler](https://apscheduler.readthedocs.org) process that schedules jobs (e.g., update graph with new datasets) on the `worker` at specified intervals
3. `worker`: An [RQ](http://python-rq.org/) worker process to run scheduled jobs
4. `redis`: A [Redis](http://redis.io) instance to act as a persistent store for the `worker`

In addition to the core infrastructure services (above), a set of monitoring/logging services are spun up. As of writing, these are mostly being used for development and testing:

1. `elasticsearch`: An [ElasticSearch](https://www.elastic.co/products/elasticsearch) instance to store, index, and support analysis of logs
2. `logstash`: A [Logstash](https://www.elastic.co/products/logstash) instance to facilitate the log pipeline
3. `kibana`: A [Kibana](https://www.elastic.co/products/kibana) instance to search and vizualize logs
4. `logspout`: A [Logspout](https://github.com/gliderlabs/logspout) instance to collect logs from the [Docker](https://www.docker.com/) containers
5. `cadvisor`: A [cAdvisor](https://github.com/google/cadvisor) instance to monitor resource usage on each [Docker](https://www.docker.com/) container

(Note: The following is not implemented)

As the service runs, an RDF dump will be continuously updated with the datasets on [DataOne](https://www.dataone.org/) which is accessible at the root of wherever the service is hosted at `/dataone.ttl`.


## What's in the graph?

For an overview of what concepts the graph contains, see the [mappings](/docs/mappings.md) documentation.

## Running

Assuming you are set up to to use [Docker](https://www.docker.com/) (see the [User Guide](https://docs.docker.com/engine/userguide/) to get set up):

```
git clone https://github.com/ec-geolink/d1lod
cd d1lod
docker-compose up # May take a while
```

After running the above `docker-compose` command, the above services should be started and available (if appropriate) on their respective ports:

1. `graphdb` → `$DOCKER_HOST:8080/openrdf-workbench/`
2. `kibana` → `$DOCKER_HOST:5601`
3. `cadvisor` → `$DOCKER_HOST:8888`

Where `$DOCKER_HOST` is `localhost` if you're running [Docker](https://www.docker.com/) natively or some IP address if you're running [Docker Machine](https://docs.docker.com/machine/). Consult the [Docker Machine](https://docs.docker.com/machine/) documentation to find this IP address.

## Testing

Tests are implemented using [PyTest](http://pytest.org/latest/). Install [PyTest](http://pytest.org/latest/) with
```
pip install pytest
```

And run the entire test suite from the root directory of this repository with:

```
py.test
```

As of writing, the test suite assumes you have a running instance of [GraphDB](http://graphdb.ontotext.com/display/GraphDB6/Home) running on `localhost:8080`. These values are hard-coded in but probably shouldn't be.
