import logging

from .client import SlinkyClient
from .constants import BACKOFF_SIZE, BATCH_SIZE

logger = logging.getLogger(__name__)


def update_job() -> None:
    """
    Checks to see if any new datasets need to be processed and if so, creates the new job
    to process.

    :return: None
    """
    logger.debug("update_job | perform()")
    client = SlinkyClient()

    if len(client.queues["default"]) > 0:
        logger.info(
            "update_job cancelled because the default queue wasn't empty which means the update_job was already running"
        )

        return

    if len(client.queues["dataset"]) >= BACKOFF_SIZE:
        logger.info(
            f"update_job cancelled because the dataset queue had more than {BACKOFF_SIZE} jobs"
        )

        return

    cursor = client.get_cursor()

    logger.debug(f"update_job | Getting datasets since {cursor}")
    datasets = client.get_new_datasets_since(cursor, BATCH_SIZE)

    logger.debug(f"update_job | Got {len(datasets)} dataset(s)")

    for dataset in datasets:
        id = dataset["identifier"]
        logger.debug(f"update_job | Enqueueing add_dataset_job for {id}")
        client.queues["dataset"].enqueue(add_dataset_job, kwargs={"id": id})

    if len(datasets) > 0:
        new_cursor = datasets[-1]["dateModified"]
        logger.debug(f"update_job | Updating cursor to {new_cursor}")
        client.set_cursor(new_cursor)


def add_dataset_job(id) -> None:
    """
    Adds a new job for processing a dataset

    :param id: The identifier of the job
    :return: None
    """
    logger.debug(f"add_dataset_job | id={id}")
    client = SlinkyClient()
    client.process_dataset(id)


def echo_job(arg):
    print(arg)