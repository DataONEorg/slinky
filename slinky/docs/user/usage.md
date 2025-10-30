# Usage

Slinky is primary built as a fully automated microservice running in a Kubernetes cluster.
However, a CLI is provided both for interacting with a running Slinky service but also for local development and testing.

## CLI

Once [installed](./installation.md), Slinky's CLI can be accessed at `slinky`.

```text
; slinky --help
Usage: slinky [OPTIONS] COMMAND [ARGS]...

  Slinky

Options:
  --help  Show this message and exit.

Commands:
  clear      Clears the graph of data.
  count      Prints the number of objects in the graph to stdout
  enqueue    Adds a dataset to the queue for processing.
  get        Processes a dataset and prints the RDF to stdout.
  insert     Processes a dataset and inserts the resulting RDF into the...
  insertall  :param debug: Set to true for debug-level debugging :return:...
  schedule   Creates a recurring scheduler to update the job queue.
  work       Creates a worker for a particular queue.
```
