# Writing Documentation

Documentation for slinky is built using Sphinx and can be authored with either RestructureText or Markdown.

## Building

To build the documentation, run the following from the `./slinky/docs` directory.

```sh
make html
```

## Writing Docs

It's helpful to have the documentation built automatically as you work instead of building it with `make html` over and over again.
To do that, use sphinx-autobuild.

From the `./slinky` directory, run:

```sh
sphinx-autobuild docs docs/_build/html
```
