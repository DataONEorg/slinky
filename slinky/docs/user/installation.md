# Installation

Slinky is not available on [PyPI](https://pypi.org/) or other package distribution channels and must be installed locally.

## Pre-requisites

Slinky is harder to install than most Python packages because it relies on the [librdf Python bindings](https://librdf.org/docs/python.html) which cannot be installed via `pip`.
See the [documenation for the Python bindings](https://librdf.org/docs/python.html) for information on how to install this package, which must be done before installing Slinky.

For users of Python installation managers such as [pyenv](https://github.com/pyenv/pyenv), extra steps may be required for the librdf Python bindings to install correctly.
Detailed documentation has been [provided separately](../developer/librdf.md).

## Installing with `pip`

Once the pre-requisites have been satisfied, the `slinky` package can be installed with:

```sh
pip install .
```
