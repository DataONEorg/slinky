FROM amoeba/redland-python:beta
LABEL Bryce Mecum <brycemecum@gmail.com>

WORKDIR /worker

ADD requirements.txt requirements.txt
COPY work.py work.py
COPY d1lod/d1lod /usr/lib/python2.7/dist-packages/d1lod

RUN pip3 install -r requirements.txt
