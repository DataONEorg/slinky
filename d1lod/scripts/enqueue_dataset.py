import os
import sys

from redis import StrictRedis
from rq import Queue

# Append parent dir so we can keep these scripts in /scripts
sys.path.insert(1, os.path.join(sys.path[0], '../'))

from d1lod import graph
from d1lod import interface
from d1lod import jobs

conn = StrictRedis(host='localhost', port='6379')
queues = {
    'default': Queue('default', connection=conn),
    'dataset': Queue('dataset', connection=conn),
    'export': Queue('export', connection=conn)
}

if __name__ == "__main__":
    identifier = "doi:10.5063/KP80JT"
    g = graph.Graph('localhost', 8890, 'geolink')
    i = interface.Interface(g)

    queues['dataset'].enqueue(jobs.add_dataset, g, i, identifier)

