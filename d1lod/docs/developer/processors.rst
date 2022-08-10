Processors
==========

The core of what Slinky does is defined by Processors.
Slinky produces RDF data (Linked Open Data) for datasets in DataONE and every dataset is run through a single ``Processor`` which usually calls one or more parent Processors.

.. mermaid::

   flowchart LR
    SlinkyClient --> *Processor
    *Processor --> RDF

Note: ``*Processor`` above represents one or more ``Processor`` classes being called.

How It Works
------------

When SlinkyClient gets asked to processor an identifier, it:

1. Finds the DataONE Object associated with the identifier and its corresponding Format ID
2. Consults the ``FORMAT_MAP`` in ``d1lod.client`` to find the right ``Processor`` to call
3. Calls that ``Processor``
4. The directly called ``Processor`` calls all arent processors until calling the final ``Processor`` class

For example, when ``SlinkyClient`` proccesses an EML 2.2.0 document, it directly calls ``EML220Processor`` which calls ``EMLProcessor`` which finally calls ``Processor``:

.. autoclasstree:: d1lod.processors.eml.eml220_processor

Each processor in the chain handles different pieces of the resulting RDF data that's produced:

- ``EML220Processor``: Specific features of EML 2.2.0
- ``EMLProcessor``: Common features of all EML 2+ documents
- ``Processor``: Common features of all DataONE Data Packages
