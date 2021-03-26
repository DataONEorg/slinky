import time
import logging
logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] [%(levelname)s] %(message)s')

from redis import StrictRedis
from rq import Worker, Queue, Connection

import sys
# Manually add d1lod since it was copied & not installed with pip
sys.path.append('/usr/lib/python3.9/dist-packages/d1lod')
from d1lod import jobs

conn = StrictRedis(host='redis', port='6379')
queues = {
    'default': Queue('default', connection=conn),
    'dataset': Queue('dataset', connection=conn),
    'export': Queue('export', connection=conn)
}

if __name__ == '__main__':
    time.sleep(10)
    with Connection(conn):
        logging.info("Worker is processing redis jobs.")
        qs = [queues[q] for q in queues]
        w = Worker(qs)
        w.work()
