import sys
import time
import logging
logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] [%(levelname)s] %(message)s')

from redis import StrictRedis
from rq import Worker, Queue, Connection

sys.path.append('/d1lod')
from d1lod import jobs

conn = StrictRedis(host='redis', port='6379')

if __name__ == '__main__':
    time.sleep(10)

    with Connection(conn):
        q = Queue()
        w = Worker(q)
        w.work()
