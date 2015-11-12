import os
import sys

from redis import StrictRedis
from rq import Queue
from apscheduler.schedulers.blocking import BlockingScheduler

sys.path.append('/usr/local/d1lod')
from d1lod import jobs

redis_host = os.getenv('SERVICE_REDIS_1_PORT_6379_TCP_ADDR', 'localhost')
redis_port = os.getenv('SERVICE_REDIS_1_PORT_6379_TCP_PORT', '6379')
conn = StrictRedis(host=redis_host, port=redis_port)

q = Queue(connection=conn)

sched = BlockingScheduler()

@sched.scheduled_job('interval', minutes=1)
def timed_job():
    print('This job is run every minute.')


@sched.scheduled_job('interval', minutes=3)
def another_timed_job():
    print('This job is run every three minutes.')

@sched.scheduled_job('interval', minutes=5)
def debug_job():
    print('DEBUG JOB BEING RUN')
    q.enqueue(jobs.debug_job)



# @sched.scheduled_job('cron', day_of_week='mon-fri', hour=17)
# def scheduled_job():
#     print('This job is run every weekday at 5pm.')

sched.start()
