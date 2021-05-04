import time
import logging

logging.basicConfig(level=logging.DEBUG)

from redis import StrictRedis
from rq import Queue
from apscheduler.schedulers.blocking import BlockingScheduler


import sys

# Manually add d1lod since it was copied & not installed with pip
sys.path.append("/usr/lib/python3.9/dist-packages/d1lod")
from d1lod import jobs

conn = StrictRedis(host="redis", port="6379")
queues = {
    "default": Queue("default", connection=conn),
    "dataset": Queue("dataset", connection=conn),
    "export": Queue("export", connection=conn),
}

sched = BlockingScheduler()


@sched.scheduled_job("interval", id="update", minutes=1)
def queue_update_job():
    queues["default"].enqueue(jobs.update_graph)


@sched.scheduled_job("interval", id="stats", minutes=1)
def queue_stats_job():
    queues["default"].enqueue(jobs.calculate_stats)


@sched.scheduled_job("interval", id="export", hours=1)
def queue_export_job():
    queues["export"].enqueue(jobs.export_graph)


# Wait a bit for Sesame to start DEVNOTE: Maybe not needed
time.sleep(10)

# Queue the stats job first. This creates the graph before any other
# jobs are run.
queues["default"].enqueue(jobs.calculate_stats)
queues["default"].enqueue(jobs.update_graph)

# Start the scheduler
sched.start()
