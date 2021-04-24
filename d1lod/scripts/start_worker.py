import sys
import time
import logging
logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] [%(levelname)s] %(message)s')

from redis import StrictRedis
from rq import Worker, Queue, Connection

sys.path.append('../d1lod')
from d1lod import jobs

conn = StrictRedis(host='localhost', port='6379')
queues = {
    'default': Queue('default', connection=conn),
    'dataset': Queue('dataset', connection=conn),
    'export': Queue('export', connection=conn)
}

if __name__ == '__main__':
    with Connection(conn):
        qs = [queues[q] for q in queues]
        w = Worker(qs)
        w.work()
