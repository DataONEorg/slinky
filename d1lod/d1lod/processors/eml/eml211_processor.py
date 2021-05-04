import logging
from .eml_processor import EMLProcessor

logger = logging.getLogger(__name__)


class EML211Processor(EMLProcessor):
    def __init__(self, client, model, sysmeta, scimeta, parts):
        super().__init__(client, model, sysmeta, scimeta, parts)

    def process(self):
        logger.debug(f"EML211Processor.process '{self.identifier}'")

        return super().process()
