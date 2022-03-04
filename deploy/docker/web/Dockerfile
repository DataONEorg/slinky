FROM slinkythegraph/slinky

RUN apt-get update -y

WORKDIR /web
ADD requirements.txt requirements.txt
ADD . .
RUN python3 -m pip install -r requirements.txt

EXPOSE 80

CMD ["uvicorn", "--host", "0.0.0.0", "--port", "80", "--proxy-headers", "app:app"]