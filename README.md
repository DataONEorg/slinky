# Slinky, the DataONE Graph Store

## Overview
Service for the DataONE Linked Open Data graph.

This repository contains the deployment and code that makes up the
DataONE graph store. 

The main infrastructure of the service is composed of four services:

1. `virtuoso`: Acts as the backend graph store
2. `scheduler`: An [APSchduler](https://apscheduler.readthedocs.org) process that schedules jobs (e.g., update graph with new datasets) on the `worker` at specified intervals
3. `worker`: An [RQ](http://python-rq.org/) worker process to run scheduled jobs
4. `redis`: A [Redis](http://redis.io) instance to act as a persistent store for the `worker` and for saving application state


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


## Deployment Management

### Kubernetes Helm

The entire stack can be deployed using the Kubernetes Helm Chart using
the following command from the `deploy/` directory.

`helm install ./ --generate-name`

To tear the helm stack down, run

`helm uninstall <name_of_the_deployment>`


### As Individual Services & Pods

The stack can also be brought up by invoking the pods and services
individually.

#### Redis
```
kubectl apply -f templates/deployment/redis-deployment.yaml
kubectl apply -f templates/service/redis-service.yaml
```

#### Virtuoso
```
kubectl apply -f templates/deployment/virtuoso-deployment.yaml
kubectl apply -f templates/service/virtuoso-service.yaml
```

#### worker
```
kubectl apply -f templates/deployment/worker-deployment.yaml
```

#### Scheduler
```
kubectl apply -f templates/deployment/scheduler-deployment.yaml
```

### Scaling Pods
The pods should be scaled the usual way, 
```
kubectl scale --replicas=0 deployments/{pod-name} 
```

Note that there should always be at least one replica running for each
pod.

### Accessing Virtuoso on Dev
Assuming that development deployments are using `minikube`, the
following command needs to be run to expose the Virtuoso service.

```
minikube service virtuoso
```

After running the command, minikube will open a browser window to the
local Virtuoso instance.

## Testing

Tests are written using [PyTest](http://pytest.org/latest/). Install [PyTest](http://pytest.org/latest/) with

```
pip install pytest
cd d1lod
py.test
```

As of writing, only tests for the supporting Python package (in directory './d1lod') have been written.
Note: The test suite assumes you have a running instance of [OpenRDF Sesame](http://rdf4j.org) running on http://localhost:8080 which means the Workbench is located at http://localhost:8080/openrdf-workbench and the Sesame interface is available at http://localhost:8080/openrdf-sesame.
