# Development Guidelines

This is a working document of developer guidelines.
Some of these may be aspirational.

## URIs

Try not to hard-code any term URIs and instead use RDFLib's [Namespace](https://rdflib.readthedocs.io/en/stable/namespaces_and_bindings.html) class. Add new namespaces to `namespaces.py.



## Exception Handling

In `Processor` classes, prefer throwing exceptions over logging and continuing when you encounter an unhandled state. The processors run in a delayed job system and so there's no harm in throwing an unhandled exception and it makes it easy to find holes in processing code.

## Exception Classes

Use and create new custom Exception classes when possible.
Put them in `./slinky/exceptions.py`.
