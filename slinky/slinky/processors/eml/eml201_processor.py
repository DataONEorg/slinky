import logging
from .eml_processor import EMLProcessor

logger = logging.getLogger(__name__)


class EML201Processor(EMLProcessor):
    """
    Class for processing EML 2.0.1. There aren't any changes between 2.0.0 and 2.0.1 that
    effect the graph pattern, so the 2.0.0 processor is used.
    """

    def __init__(self, client, model, sysmeta, scimeta, parts):
        super().__init__(client, model, sysmeta, scimeta, parts)

    def process(self):
        logger.debug(f"EML201Processor.process '{self.identifier}'")
        # Use the 2.0.0 processor
        return super().process()
