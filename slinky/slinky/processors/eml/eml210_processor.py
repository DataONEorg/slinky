import logging
from .eml_processor import EMLProcessor

logger = logging.getLogger(__name__)


class EML210Processor(EMLProcessor):
    """
    Class for processing EML 2.1.0 documents. There aren't any changes
    between 2.0.0 and 2.1.0 that effect the current graph pattern, so the base
    processor is used.
    """

    def __init__(self, client, model, sysmeta, scimeta, parts):
        super().__init__(client, model, sysmeta, scimeta, parts)

    def process(self):
        logger.debug(f"EML210Processor.process '{self.identifier}'")

        return super().process()
