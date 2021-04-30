import logging
from .eml_processor import EMLProcessor

logger = logging.getLogger(__name__)


class EML220Processor(EMLProcessor):
    def __init__(self, model, sysmeta, scimeta, parts):
        super().__init__(model, sysmeta, scimeta, parts)

    def process(self):
        logger.debug("EML220Processor.process")
        return super().process()
