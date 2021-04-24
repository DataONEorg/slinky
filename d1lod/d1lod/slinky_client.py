from contextlib import contextmanager
import RDF
from filtered_client import FilteredCoordinatingNodeClient
from urllib.parse import quote_plus as q
import logging

logging.basicConfig(level=logging.DEBUG)


### SparqlTripleStore
class SparqlTripleStore:
    def __init__(self):
        pass

### Processors
class Processor:
    def __init__(self, model, sysmeta, scimeta, parts):
        self.model = model
        self.sysmeta = sysmeta
        self.scimeta = scimeta
        self.parts = parts


    def process_parts(self):
        for part in self.parts:
            # Skip self
            if part.identifier.value() == self.sysmeta.identifier.value():
                logging.info("Skipping part with identifier {} because it's the same as the dataset identifier {}".format(part.identifier.value(), self.sysmeta.identifier.value()))
                continue

            part_subject = RDF.Node(RDF.Uri("https://dataone.org/datasets/{}".format(q(part.identifier.value()))))

            self.model.append(RDF.Statement(
                part_subject,
                RDF.Node(RDF.Uri("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")),
                RDF.Node(RDF.Uri("https://schema.org/DataDownload"))
            ))

            self.model.append(RDF.Statement(
                part_subject,
                RDF.Node(RDF.Uri("https:schema.org/identifier")),
                RDF.Node(part.identifier.value())
            ))


class EMLProcessor(Processor):
    def __init__(self,  model, sysmeta, scimeta, parts):
        super().__init__(model, sysmeta, scimeta, parts)

    def process(self):
        logging.info("EMLProcessor.process")
        dataset_subject = RDF.Node(RDF.Uri("https://dataone.org/datasets/{}".format(q(self.sysmeta.identifier.value()))))

        self.model.append(RDF.Statement(
            dataset_subject,
            RDF.Node(RDF.Uri("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")),
                RDF.Node(RDF.Uri("https://schema.org/Dataset"))
         ))

        self.model.append(RDF.Statement(
            dataset_subject,
            RDF.Node(RDF.Uri("https:schema.org/identifier")),
            RDF.Node(self.sysmeta.identifier.value())
        ))

        for name in self.scimeta.findall(".//dataset/title"):
            self.model.append(RDF.Statement(
                dataset_subject,
                RDF.Node(RDF.Uri("https:schema.org/name")),
                RDF.Node(name.text)
            ))

        for description in self.scimeta.findall(".//dataset/abstract"):
            self.model.append(RDF.Statement(
                dataset_subject,
                RDF.Node(RDF.Uri("https:schema.org/description")),
                RDF.Node("".join([item.text for item in description.iter()]).strip())
            ))

        self.process_parts()

        return self.model


    def process_parts(self):
        super().process_parts()


class EML211Processor(EMLProcessor):
    def __init__(self, model, sysmeta, scimeta, parts):
        super().__init__(model, sysmeta, scimeta, parts)


    def process(self):
        logging.info("EML211Processor.process")
        return super().process()


class EML220Processor(EMLProcessor):
    def __init__(self, model, sysmeta, scimeta, parts):
        super().__init__(model, sysmeta, scimeta, parts)


    def process(self):
        logging.info("EML220Processor.process")
        return super().process()


FORMAT_MAP = {
    "eml://ecoinformatics.org/eml-2.1.1": EML211Processor,
    "https://eml.ecoinformatics.org/eml-2.2.0": EML220Processor
}


### Exceptions
class UnsupportedFormatException(Exception):
    pass


class UnsupportedPackageScenario(Exception):
    pass


### SlinkyClient
class SlinkyClient:
    def __init__(self):
        self.d1client = FilteredCoordinatingNodeClient({
            'q':'formatType:METADATA AND -obsoletedBy:*',
            'rows': '1000',
            'fl': 'identifier',
            'wt': 'json'
        })
        self.store = SparqlTripleStore()


    def process_dataset(self, identifier):
        return self.get_model_for_dataset(identifier)


    def get_model_for_dataset(self, identifier):
        storage = RDF.MemoryStorage()
        model = RDF.Model(storage)

        # Get System Metadata
        sysmeta = self.d1client.get_system_metadata(identifier)

        # Get Science Metadata
        science_metadata = self.d1client.get_object(sysmeta)

        # Get Data Package parts (members)
        part_ids = self.d1client.get_parts(identifier)
        parts = [self.d1client.get_system_metadata(identifier) for identifier in part_ids]

        # Process based on formatID
        if not sysmeta.formatId in FORMAT_MAP:
            raise UnsupportedFormatException("Unsupported format {}" % sysmeta.formatID)

        processor = FORMAT_MAP[sysmeta.formatId](model, sysmeta, science_metadata, parts)
        model = processor.process()

        return model

if __name__ == "__main__":
    client = SlinkyClient()
    model = client.process_dataset("doi:10.18739/A2C824F9X")

    serializer = RDF.TurtleSerializer()
    print(serializer.serialize_model_to_string(model))

