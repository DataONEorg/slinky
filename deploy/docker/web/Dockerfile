FROM ghcr.io/dataoneorg/slinky:0.3.0

WORKDIR /web
ADD requirements.txt requirements.txt
ADD . .
RUN python3 -m pip install -r requirements.txt --user

EXPOSE 8080

CMD ["uvicorn", "--host", "0.0.0.0", "--port", "8080", "--proxy-headers", "app:app"]
