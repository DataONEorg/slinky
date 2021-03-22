FROM python:2.7-jessie
MAINTAINER Bryce Mecum <brycemecum@gmail.com>

RUN apt-get update && apt-get install -y python-librdf

WORKDIR /scheduler

ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY schedule.py schedule.py
COPY d1lod/d1lod/ /usr/lib/python2.7/dist-packages/d1lod
