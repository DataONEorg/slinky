from d1lod.stores.local_store import LocalStore
import RDF
from redis import Redis
import logging
from rq import Queue
from datetime import datetime, timezone

from .filtered_d1_client import FilteredCoordinatingNodeClient
from .exceptions import UnsupportedFormatException, CursorSetFailedException
from .processors.eml.eml211_processor import EML211Processor
from .processors.eml.eml220_processor import EML220Processor
from .processors.iso.iso_processor import ISOProcessor
from .settings import FILTERS, REDIS_HOST, REDIS_PORT, GRAPH_HOST, GRAPH_PORT
from .constants import SLINKY_CURSOR_KEY, CURSOR_EPOCH
from .stores.local_store import LocalStore
from .stores.virtuoso_store import VirtuosoStore

logger = logging.getLogger(__name__)


FORMAT_MAP = {
    "eml://ecoinformatics.org/eml-2.1.1": EML211Processor,
    "https://eml.ecoinformatics.org/eml-2.2.0": EML220Processor,
    "http://www.isotc211.org/2005/gmd": ISOProcessor,
}


class SlinkyClient:
    def __init__(self, data_filter=FILTERS["sasap"], local_store: bool = False):
        """
        Create a new SlinkyClient

        :param data_filter: The filter that will restrict DataONE search results
        :param local_store Set when Slinky should be using the LocalStore graph store
        """
        # The client used to communicate with DataONE
        self.d1client = FilteredCoordinatingNodeClient(data_filter)
        # The backing graph store. If there isn't a graph endpoint, use the local store
        if local_store:
            self.store = LocalStore()
        else:
            self.store = VirtuosoStore(endpoint=f"{GRAPH_HOST}:{GRAPH_PORT}")
        # If there's a redis endpoint use it, otherwise ignore redis
        self.redis = Redis(host=REDIS_HOST, port=REDIS_PORT)

        if self.redis:
            self.queues = self.get_queues()

    def get_queues(self):
        return {
            "default": Queue("default", connection=self.redis),
            "dataset": Queue("dataset", connection=self.redis),
        }

    def process_dataset(self, identifier):
        model = self.get_model_for_dataset(identifier)
        self.store.insert_model(model)

    def get_model_for_dataset(self, identifier):
        logger.debug(f"SlinkyClient.get_model_for_dataset | {identifier}")

        storage = RDF.MemoryStorage()
        model = RDF.Model(storage)

        sysmeta = self.d1client.get_system_metadata(identifier)
        science_metadata = self.d1client.get_object(sysmeta)

        # Get Data Package parts (members)
        part_ids = self.d1client.get_parts(identifier)
        parts = [
            self.d1client.get_system_metadata(identifier) for identifier in part_ids
        ]

        # Process based on formatID
        if not sysmeta.formatId in FORMAT_MAP:
            raise UnsupportedFormatException(f"Unsupported format {sysmeta.formatId}")

        processor = FORMAT_MAP[sysmeta.formatId](
            self, model, sysmeta, science_metadata, parts
        )

        logging.info(
            "Getting model for dataset '{}' with processor '{}'".format(
                identifier, type(processor).__name__
            )
        )

        return processor.process()

    def get_new_datasets_since(self, datetime_str, batch_size=100):
        return self.d1client.query(
            {
                "q": f"dateModified:{{{datetime_str} TO NOW]",
                "sort": "dateModified asc",
                "rows": str(batch_size),
                "fl": "identifier,dateModified",
            }
        )

    def get_cursor(self):
        cursor = self.redis.get(SLINKY_CURSOR_KEY)

        if cursor is not None:
            return cursor.decode("utf-8")

        return CURSOR_EPOCH

    def set_cursor(self, value):
        result = self.redis.set(SLINKY_CURSOR_KEY, value)

        if result is None:
            raise CursorSetFailedException

    def generate_cursor_datetime_string(self):
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
