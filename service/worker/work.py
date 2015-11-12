import os
import sys

from redis import StrictRedis
from rq import Worker, Queue, Connection

sys.path.append('/usr/local/d1lod')
from d1lod import jobs

listen = ['high', 'default', 'low']

redis_host = os.getenv('SERVICE_REDIS_1_PORT_6379_TCP_ADDR', 'localhost')
redis_port = os.getenv('SERVICE_REDIS_1_PORT_6379_TCP_PORT', '6379')
print "%s:%s" % (redis_host, redis_port)

conn = StrictRedis(host=redis_host, port=redis_port)

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()
