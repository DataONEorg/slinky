import os
import sys
import time

from redis import StrictRedis
from rq import Worker, Queue, Connection

sys.path.append('/usr/local/d1lod')
from d1lod import jobs

conn = StrictRedis(host='redis', port='6379')

if __name__ == '__main__':
    time.sleep(10)

    with Connection(conn):
        q = Queue()
        w = Worker(q)
        w.work()
