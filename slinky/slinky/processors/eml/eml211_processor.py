import logging
from .eml_processor import EMLProcessor

logger = logging.getLogger(__name__)


class EML211Processor(EMLProcessor):
    """
    Class for processing EML 2.1.1. For the moment, the graph pattern is agnostic of the
    changes in 2.1.1. The 2.0.0 processor is used.
    """

    def __init__(self, client, model, sysmeta, scimeta, parts):
        super().__init__(client, model, sysmeta, scimeta, parts)

    def process(self):
        logger.debug(f"EML211Processor.process '{self.identifier}'")

        return super().process()
