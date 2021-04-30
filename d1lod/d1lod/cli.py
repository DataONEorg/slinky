import click
import logging

from .client import SlinkyClient
from .jobs import add_dataset_job, update_job


@click.command()
@click.option("--count", default=1, help="Number of greetings.")
@click.option("--name", prompt="Your name", help="The person to greet.")
def hello(count, name):
    """Simple program that greets NAME for a total of COUNT times."""
    for x in range(count):
        click.echo("Hello %s!" % name)


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

    client = SlinkyClient()
    model = client.get_model_for_dataset(id)

    import RDF

    serializer = RDF.TurtleSerializer()
    print(serializer.serialize_model_to_string(model))


@cli.command()
@click.argument("queue")
def work(queue):
    from rq import Worker, Queue, Connection

    client = SlinkyClient()

    with Connection(client.redis):
        default = Worker(client.queues[queue])
        default.work()


@cli.command()
@click.argument("id")
def add(id):
    from rq import Worker, Queue, Connection

    client = SlinkyClient()
    client.queues["dataset"].enqueue(add_dataset_job, id)


@cli.command()
def schedule():
    from redis import Redis
    from rq_scheduler import Scheduler
    import datetime

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
