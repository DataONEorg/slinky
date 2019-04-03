"""
Process a dataset (by PID) for dataset/people/org triples.
"""


import os
import sys

# Append parent dir so we can keep these scripts in /scripts
sys.path.insert(1, os.path.join(sys.path[0], '../'))

from d1lod import graph
from d1lod import interface

if __name__ == "__main__":
    identifier = 'doi:10.6085/AA/YB15XX_015MU12004R00_20080619.50.1'

    g = graph.Graph('localhost', 8890, 'geolink')
    i = interface.Interface(g)

    i.addDataset(identifier)
