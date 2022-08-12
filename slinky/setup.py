#!/usr/bin/env python

from distutils.core import setup
from setuptools import setup, find_packages

setup(
    name="slinky",
    version="0.3.0",
    description="A library for running the Slink.",
    author="Bryce Mecum",
    author_email="mecum@nceas.ucsb.edu",
    license="Apache License, Version 2.0",
    url="https://github.com/dataoneorg/slinky",
    packages=find_packages(exclude=("tests",)),
    python_requires=">=3.6",
    install_requires=[
        "httpx",
        "rq",
        "rq-scheduler",
        "dataone.libclient",
        "redis",
        "Click",
        "tdqm",
        "rdflib",
        "rdflib-jsonld",
    ],
    entry_points="""
        [console_scripts]
        slinky=slinky.cli:cli
    """,
    extras_require={
        "docs": ["sphinx", "furo", "myst-parser", "sphinxcontrib-mermaid"],
        "test": [
            "pytest",
            "black",
        ],
    },
)
