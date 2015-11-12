FROM python:2.7.10
MAINTAINER Bryce Mecum <brycemecum@gmail.com>

ADD . /usr/local/worker
WORKDIR /usr/local/worker

RUN pip install -r requirements.txt

CMD [ "python", "work.py" ]
