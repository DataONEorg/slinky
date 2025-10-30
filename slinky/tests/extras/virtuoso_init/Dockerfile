FROM openlink/virtuoso-opensource-7

RUN apt-get update && \
  apt-get install -y \
  curl

ADD entrypoint.sh /entrypoint.sh

CMD [ "/bin/bash", "/entrypoint.sh" ]
