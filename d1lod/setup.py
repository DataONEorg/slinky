#!/usr/bin/env python

from distutils.core import setup

setup(name='d1lod',
      version='0.1',
      description='A library for running the DataOne LOD service.',
      author='Bryce Mecum',
      author_email='mecum@nceas.ucsb.edu',
      url='https://github.com/ec-geolink/d1lod',
      packages=['d1lod', 'd1lod.sesame', 'd1lod.people'],
     )
