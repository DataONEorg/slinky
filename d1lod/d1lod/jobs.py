from datetime import datetime, timezone
import logging

from .client import SlinkyClient
from .constants import SLINKY_CURSOR_KEY
from .exceptions import CursorSetFailedException

logger = logging.getLogger(__name__)


BATCH_SIZE = 200
CURSOR_EPOCH = "1900-01-01T00:00:00.000Z"

client = SlinkyClient(
    filter={
        "q": 'datasource:"urn:node:KNB" AND project:"State of Alaska\'s Salmon and People" AND formatType:METADATA AND -obsoletedBy:*',
    }
)


def get_cursor():
    cursor = client.redis.get(SLINKY_CURSOR_KEY)

    if cursor is not None:
        return cursor.decode("utf-8")

    return CURSOR_EPOCH


def set_cursor(value):
    result = client.redis.set(SLINKY_CURSOR_KEY, value)

    if result is None:
        raise CursorSetFailedException


def generate_cursor_datetime_string():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def update_job():
    # TODO: Ensure we're the only updatejob on the queue
    logger.debug(f"update_job | perform()")

    cursor = get_cursor()

    logger.debug(f"update_job | Getting datasets since {cursor}")
    datasets = client.get_new_datasets_since(cursor, BATCH_SIZE)

    logger.debug(f"update_job | Got {len(datasets)} dataset(s)")

    for dataset in datasets:
        id = dataset["identifier"]
        logger.debug(f"update_job | Enqueueing add_dataset_job for {id}")
        client.queues["dataset"].enqueue(add_dataset_job, id)

    if len(datasets) > 0:
        new_cursor = datasets[-1]["dateModified"]
        logger.debug(f"update_job | Updating cursor to {new_cursor}")
        set_cursor(new_cursor)


def add_dataset_job(id):
    logger.debug(f"add_dataset_job | id={id}")

    client = SlinkyClient()
    client.process_dataset(id)


def echo_job(arg):
    print(arg)
