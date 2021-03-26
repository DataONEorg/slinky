FROM amoeba/redland-python:beta
LABEL Bryce Mecum <brycemecum@gmail.com>

WORKDIR /worker

ADD requirements.txt requirements.txt
ADD work.py work.py
ADD ./d1lod/d1lod /usr/local/lib/python3.9/dist-packages/d1lod/

RUN pip3 install -r requirements.txt
