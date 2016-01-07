import sys
import time
import logging
logging.basicConfig(level=logging.DEBUG)

from redis import StrictRedis
from rq import Queue
from apscheduler.schedulers.blocking import BlockingScheduler

from d1lod import jobs

conn = StrictRedis(host='redis', port='6379')
queues = {
    'low': Queue('low', connection=conn),
    'medium': Queue('medium', connection=conn),
    'high': Queue('high', connection=conn)
}

sched = BlockingScheduler()


@sched.scheduled_job('interval', minutes=1)
def queue_update_job():
    queues['medium'].enqueue(jobs.update_graph)


@sched.scheduled_job('interval', minutes=1)
def queue_stats_job():
    queues['high'].enqueue(jobs.calculate_stats)


@sched.scheduled_job('interval', minutes=1)
def queue_export_job():
    queues['high'].enqueue(jobs.export_graph)


@sched.scheduled_job('interval', minutes=1)
def print_jobs_job():
    sched.print_jobs()

# Wait a bit for Sesame to start
time.sleep(10)

# Queue the stats job first. This creates the repository before any other
# jobs are run.
queues['high'].enqueue(jobs.calculate_stats)

# Start the scheduler
sched.start()
