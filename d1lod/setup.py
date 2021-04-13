#!/usr/bin/env python

from distutils.core import setup

setup(name='d1lod',
      version='0.2',
      description='A library for running the Slink.',
      author='Bryce Mecum',
      author_email='mecum@nceas.ucsb.edu',
      url='https://github.com/dataoneorg/slinky',
      packages=['d1lod', 'd1lod.virtuoso', 'd1lod.people'],
     )
