import sys
import time
import logging
logging.basicConfig(level=logging.DEBUG)

from redis import StrictRedis
from rq import Queue
from apscheduler.schedulers.blocking import BlockingScheduler

sys.path.append('/d1lod')
from d1lod import jobs

conn = StrictRedis(host='redis', port='6379')
q = Queue(connection=conn)

sched = BlockingScheduler()

@sched.scheduled_job('interval', minutes=1)
def timed_job():
    print('This job is run every 1 minute.')

@sched.scheduled_job('interval', minutes=1)
def debug_job():
    q.enqueue(jobs.update_graph)

@sched.scheduled_job('interval', hours=1)
def debug_job():
    q.enqueue(jobs.calculate_stats)

@sched.scheduled_job('interval', hours=1)
def export_job():
    q.enqueue(jobs.export_graph)

@sched.scheduled_job('interval', minutes=1)
def debug_job():
    sched.print_jobs()

time.sleep(10)
sched.start()
