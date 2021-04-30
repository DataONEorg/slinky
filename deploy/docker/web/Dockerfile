FROM amoeba/redland-python:beta
LABEL Bryce Mecum <brycemecum@gmail.com>

RUN apt-get update -y

ADD d1lod /d1lod
RUN pip3 install /d1lod

WORKDIR /web
ADD requirements.txt requirements.txt
ADD app.py app.py
RUN pip3 install -r requirements.txt

EXPOSE 80

CMD ["uvicorn", "--host", "0.0.0.0", "--port", "80", "app:app"]
