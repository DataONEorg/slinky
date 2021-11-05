import click
from redis import Redis
from rq_scheduler import Scheduler
import datetime
import logging

from .client import SlinkyClient
from .jobs import add_dataset_job, update_job
from .settings import ENVIRONMENTS
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
@click.option(
    "--format", default="turtle", help="One of turtle, ntriples, rdfxml, or jsonld"
)
def get(debug, count, format, id):
    if debug:
        logging.basicConfig(level=logging.DEBUG)

    if not format in ["turtle", "ntriples", "rdfxml", "jsonld"]:
        raise SerializationFormatNotSupported(format)

    client = SlinkyClient(environment=ENVIRONMENTS["cli"])
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
def insert(debug, id):
    if debug:
        logging.basicConfig(level=logging.DEBUG)

    client = SlinkyClient(environment=ENVIRONMENTS["development"])
    client.process_dataset(id)

    return None


@cli.command()
@click.option("--debug", is_flag=True, default=False)
def insertall(debug):
    if debug:
        logging.basicConfig(level=logging.DEBUG)

    client = SlinkyClient(environment=ENVIRONMENTS["development"])
    datasets = client.get_new_datasets_since("1900-01-01T00:00:00.000Z")

    from tqdm import trange

    for i in trange(len(datasets)):
        id = datasets[i]["identifier"]

        try:
            client.process_dataset(id)
        except:
            print(f"Failed to insert {id}")


@cli.command()
def clear():
    client = SlinkyClient(environment=ENVIRONMENTS["development"])
    old_size = client.store.count()
    client.store.clear()
    new_size = client.store.count()

    print(f"Removed {old_size - new_size} triples. New count: {new_size} triple(s).")


@cli.command()
def count():
    client = SlinkyClient(environment=ENVIRONMENTS["development"])

    print(client.store.count())


@cli.command()
@click.argument("queue")
@click.option("--debug", is_flag=True, default=False)
@click.option("--prod", is_flag=True, default=False)
def work(debug: bool, queue, prod: bool):
    """
    Creates a worker for a particular queue.

    :param debug: Flag that when set will provide extra logging
    :param queue: The name of the queue that this worker associates with
    :param prod: A flag which when set to true uses production networking settings
    :return: None
    """
    if debug:
        logging.basicConfig(level=logging.DEBUG)

    from rq import Worker, Connection

    environment = 'production' if prod else "development"
    client = SlinkyClient(environment=ENVIRONMENTS[environment])

    with Connection(client.redis):
        default = Worker(client.queues[queue])
        default.work()


@cli.command()
@click.argument("id")
def enqueue(id):
    client = SlinkyClient()
    client.queues["dataset"].enqueue(add_dataset_job, id)


@cli.command()
@click.argument("id")
@click.option("--debug", is_flag=True, default=False)
def insert(debug, id):
    if debug:
        logging.basicConfig(level=logging.DEBUG)

    client = SlinkyClient(environment=ENVIRONMENTS["development"])
    client.process_dataset(id)


@cli.command()
@click.option("--prod", is_flag=True, default=False)
def schedule(prod: bool):
    """
    Creates a recurring scheduler to update the job queue.

    :param prod: Flag that when set to true uses the production kubernetes networking settings
    :return: None
    """
    scheduler = Scheduler("default", connection=Redis(host='redis')) if prod \
        else Scheduler("default", connection=Redis())

    for job in scheduler.get_jobs():
        print(f"Canceling existing job {job.id}")
        scheduler.cancel(job)

    job = scheduler.schedule(
        scheduled_time=datetime.datetime.utcnow(),
        func=update_job,
        kwargs={'prod': prod},
        interval=60,
        repeat=None,
    )

    print(f"Scheduled job {job.id}")


if __name__ == "__main__":
    cli()
