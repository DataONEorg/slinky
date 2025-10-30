# Slinky Helm Chart

## Installation

### Pre-requisites

- A Kubernetes cluster
- Helm

### Quick-Start

```sh
helm install slinky .
```

### Ingress

The Slinky chart supports setting up an Ingress, provided your cluster is set up to create and set up Ingress resources.

To install the chart with Ingress, you must provide the following values in your `helm install` command:

- `ingress.enabled`
- `ingress.host`
- `ingress.tls.secretName`
- `ingress.clusterIssuer`

As an example,

```sh
helm install \
    --set ingress.enabled=true \
    --set ingress.host=api.example.org \
    --set ingress.tls.secretName=my-tls-secret-name \
    --set ingress.clusterIssuer=my-cluster-issuer \
    slinky .
```

