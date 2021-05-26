import click
from redis import Redis
from rq_scheduler import Scheduler
import datetime
import logging

from .client import SlinkyClient
from .jobs import add_dataset_job, update_job
from .settings import ENVIRONMENTS


@click.group()
def cli():
    """
    Slinky
    """


@cli.command()
@click.argument("id")
@click.option("--debug", is_flag=True, default=False)
def get(debug, id):
    if debug:
        logging.basicConfig(level=logging.DEBUG)

    client = SlinkyClient(environment=ENVIRONMENTS["cli"])
    model = client.get_model_for_dataset(id)

    import RDF

    serializer = RDF.TurtleSerializer()
    model_as_string = serializer.serialize_model_to_string(model)

    print(model_as_string)


@cli.command()
@click.argument("queue")
@click.option("--debug", is_flag=True, default=False)
def work(debug, queue):
    if debug:
        logging.basicConfig(level=logging.DEBUG)

    from rq import Worker, Connection

    client = SlinkyClient()

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

    client = SlinkyClient()
    client.process_dataset(id)


@cli.command()
def schedule():
    scheduler = Scheduler("default", connection=Redis())

    for job in scheduler.get_jobs():
        print(f"Canceling existing job {job.id}")
        scheduler.cancel(job)

    job = scheduler.schedule(
        scheduled_time=datetime.datetime.utcnow(),
        func=update_job,
        interval=300,
        repeat=None,
    )

    print(f"Scheduled job {job.id}")


if __name__ == "__main__":
    cli()
