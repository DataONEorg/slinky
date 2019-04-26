FROM python:2.7-jessie
MAINTAINER Bryce Mecum <brycemecum@gmail.com>

RUN apt-get update && apt-get install -y python-pip

RUN pip install rq-dashboard

WORKDIR /
COPY run.sh /run.sh
RUN chmod 755 /run.sh

EXPOSE 9181

CMD [ "/run.sh" ]
