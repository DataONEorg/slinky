# Kubernetes Deployment

## Architecture

At a high level, the Slinky stack is a collection of five deployments
and two services shown below.

![k8 deployement diagram](diagrams/deployments.png)

![k8 service diagram](diagrams/services.png)


### Deployments

In general, the deployments in Slinky are all very similar, which should
be visually clear in the architecture diagrams below.

#### With Services
These deployments need to accept connections from other applications,
which might be end users _or_ other applications in the stack. Because
of this requirement, these deployments are associated with a service.
    
![k8 Deployement diagram for redis](diagrams/redis.png)

![k8 Deployement diagram for Virtuoso](diagrams/virtuoso.png)

#### Without Services

These deployments don't handle traffic from exernal applications, hence
the deployment diagrams are without services. 

![k8 Deployement diagram for the scheduler](diagrams/scheduler.png)

![k8 Deployment diagram for the worker](diagrams/worker.png)

When a worker deployment is scaled, the vertical scaling is evident in
the following diagram which shows a worker deployment with a replica
count of 3.

![k8 Deployment diagram for a scaled worker](diagrams/scaled-worker.png)

### Filesystem Artifacts

All of the Slinky deployments use a single volume claim which has space
allocated on the CephFS system, shown below.

![k8 Volume management diagram](diagrams/volume.png)