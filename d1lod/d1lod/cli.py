import click
from redis import Redis, ConnectionError
import requests
from rq_scheduler import Scheduler
from time import sleep
import datetime
import logging

from .client import SlinkyClient
from .jobs import add_dataset_job, update_job
from .settings import REDIS_HOST, REDIS_PORT, GRAPH_HOST, GRAPH_PORT
from .exceptions import SerializationFormatNotSupported


@click.group()
def cli():
    """
    Slinky
    """

@cli.command()
@click.argument("id")
@click.option("--debug", is_flag=True, default=False)
@click.option("--count", is_flag=True, default=False)
@click.option("--format", default="turtle", help="One of turtle, ntriples, rdfxml, or jsonld")
def get(debug: bool, count, format: str, id) -> None:
    """
    Processes a dataset and prints the RDF to stdout.

    :param debug: Set to true for debug-level debugging
    :param count:
    :param format: The format of the resulting RDF
    :param id: The identifier of the dataset
    :return: None
    """
    if debug:
        logging.basicConfig(level=logging.DEBUG)

    if not format in ["turtle", "ntriples", "rdfxml", "jsonld"]:
        raise SerializationFormatNotSupported(format)

    client = SlinkyClient(local_store=True)
    model = client.get_model_for_dataset(id)

    if count:
        print(len(model))
        return

    import RDF

    # Handle JSON-LD as a special case
    if format == "jsonld":
        from rdflib import Graph

        # Hand off our model to RDFLib by serializing and re-parsing
        serializer = RDF.NTriplesSerializer()
        ntriples = serializer.serialize_model_to_string(model)

        # Re-parse
        graph = Graph().parse(data=ntriples, format="ntriples")

        print(graph.serialize(format="json-ld", indent=4).decode("utf-8"))

        return

    # Handle formats Redlands supports
    if format == "turtle":
        serializer = RDF.TurtleSerializer()
    elif format == "ntriples":
        serializer = RDF.NTriplesSerializer()
    elif format == "rdfxml":
        serializer = RDF.RDFXMLSerializer()

    print(serializer.serialize_model_to_string(model))


@cli.command()
@click.argument("id")
@click.option("--debug", is_flag=True, default=False)
def insert(debug: bool, id) -> None:
    """
    Processes a dataset and inserts the resulting RDF into the graph.

    :param debug: Set to true for debug-level debugging
    :param id: The identifier of the dataset being inserted
    :return: None
    """
    if debug:
        logging.basicConfig(level=logging.DEBUG)

    client = SlinkyClient()
    client.process_dataset(id)

    return None


@cli.command()
@click.option("--debug", is_flag=True, default=False)
def insertall(debug: bool) -> None:
    """

    :param debug: Set to true for debug-level debugging
    :return: None
    """
    if debug:
        logging.basicConfig(level=logging.DEBUG)

    client = SlinkyClient()
    datasets = client.get_new_datasets_since("1900-01-01T00:00:00.000Z")

    from tqdm import trange

    for i in trange(len(datasets)):
        id = datasets[i]["identifier"]

        try:
            client.process_dataset(id)
        except Exception as e:
            print(f"Failed to insert {id} due to {e}")


@cli.command()
def clear() -> None:
    """
    Clears the graph of data.

    :return: None
    """
    client = SlinkyClient()
    old_size = client.store.count()
    client.store.clear()
    new_size = client.store.count()

    print(f"Removed {old_size - new_size} triples. New count: {new_size} triple(s).")


@cli.command()
def count() -> None:
    """
    Prints the number of objects in the graph to stdout

    :return: None
    """
    client = SlinkyClient()
    print(client.store.count())


@cli.command()
@click.argument("queue")
@click.option("--debug", is_flag=True, default=False)
def work(debug: bool,  queue) -> None:
    """
    Creates a worker for a particular queue.

    :param debug: Flag that when set will provide extra logging
    :param queue: The name of the queue that this worker associates with
    :return: None
    """
    if debug:
        logging.basicConfig(level=logging.DEBUG)

    from rq import Worker, Connection
    if not _wait_for_redis(30, 10):
        logging.error(f"A connection to Redis could not be established. Exiting...")
        return

    if not _wait_for_server(GRAPH_HOST, GRAPH_PORT, 60, 10):
        logging.error("A connection to Virtuoso could not be established. Exiting...")
        return

    client = SlinkyClient()

    with Connection(client.redis):
        default = Worker(client.queues[queue])
        default.work()


@cli.command()
@click.argument("id")
def enqueue(id) -> None:
    """
    Adds a dataset to the queue for processing.

    :param local: Boolean for signaling that the in-memory graph store should be used
    :param id: The identifier of the dataset being queued
    :return: None
    """
    client = SlinkyClient()
    client.queues["dataset"].enqueue(add_dataset_job, id)


@cli.command()
@click.argument("id")
@click.option("--debug", is_flag=True, default=False)
def insert(debug:bool, id) -> None:
    if debug:
        logging.basicConfig(level=logging.DEBUG)

    client = SlinkyClient()
    client.process_dataset(id)


@cli.command()
@click.option("--debug", is_flag=True, default=False)
def schedule(debug: bool) -> None:
    """
    Creates a recurring scheduler to update the job queue.

    :param debug: Flag that when set will log debug level statements
    :return: None
    """
    # Wait for redis to come online. Try connecting twice every minute, ten times before failing
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    if not _wait_for_redis(30, 10):
        logging.error("Could not establish a connection with Redis. Exiting...")
        return

    scheduler = Scheduler("default", connection=Redis(host=REDIS_HOST))
    for job in scheduler.get_jobs():
        print(f"Canceling existing job {job.id}")
        scheduler.cancel(job)

    job = scheduler.schedule(
        scheduled_time=datetime.datetime.utcnow(),
        func=update_job,
        interval=60,
        repeat=None,
    )

    print(f"Scheduled job {job.id}")


if __name__ == "__main__":
    cli()


def _wait_for_server(server: str, port: int, timeout: int, threshold: int) -> bool:
    """
    Waits for a server to come online by connecting every <timeout> seconds. After it fails <threshold>
    times, False is returned.

    :param server: The URL of the service being waited on
    :param port: The port that the server should be contacted on
    :param timeout: The number of seconds to wait between retrying
    :param threshold: The number of times to try connecting
    :return: True when the service is reached, false if the threshold is reached
    """
    # Create headers
    headers = requests.utils.default_headers()
    headers.update({'User-Agent': 'Slinky'})
    attempt_number=0
    while attempt_number < threshold:
        attempt_number += 1
        try:
            response = requests.get(f"{server}:{port}", headers=headers)
            if response.status_code == 200:
                return True
        except requests.exceptions.RequestException:
            logging.debug(f"Waiting for server {server} to come online...")
            sleep(timeout)

    logging.debug("The server, {server}, never came online.")
    return False


def _wait_for_redis(timeout: int, threshold: int) -> bool:
    """
    Waits for redis to come online by connecting every <timeout> seconds. After it fails <threshold>
    times, False is returned.
    :param timeout: The number of seconds to wait between retrying
    :param threshold: The number of times to try connecting
    :return: True when the service is reached, false if the threshold is reached
    """
    redis_client = Redis(host=REDIS_HOST, port=REDIS_PORT)
    attempt_number=0
    while attempt_number < threshold:
        attempt_number += 1
        try:
            if redis_client.ping():
                return True
        except ConnectionError:
            logging.debug(f"Redis isn't online yet, waiting {timeout} seconds before trying again.")
            sleep(timeout)

    logging.error(f"Redis wasn't reached after {threshold} attempts")
    return False
