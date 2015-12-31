import sys
import time
import logging
logging.basicConfig(level=logging.DEBUG)

from redis import StrictRedis
from rq import Queue
from apscheduler.schedulers.blocking import BlockingScheduler

from d1lod import jobs

conn = StrictRedis(host='redis', port='6379')
q = Queue(connection=conn)

sched = BlockingScheduler()

@sched.scheduled_job('interval', minutes=1)
def queue_update_job():
    q.enqueue(jobs.update_graph, timeout=3600) # 1 hour timeout

@sched.scheduled_job('interval', minutes=1)
def queue_stats_job():
    q.enqueue(jobs.calculate_stats)

@sched.scheduled_job('interval', minutes=1)
def queue_export_job():
    q.enqueue(jobs.export_graph)

@sched.scheduled_job('interval', minutes=1)
def print_jobs_job():
    sched.print_jobs()

# Wait a bit for Sesame to start
time.sleep(10)

# Queue the stats job first. This creates the repository before any other
# jobs are run.
q.enqueue(jobs.calculate_stats)

# Start the scheduler
sched.start()
