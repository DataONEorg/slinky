FROM python:2.7.10
MAINTAINER Bryce Mecum <brycemecum@gmail.com>

RUN apt-get update && apt-get install -y python-librdf

WORKDIR /scheduler

ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY schedule.py schedule.py

CMD [ "python", "-u", "schedule.py" ]
