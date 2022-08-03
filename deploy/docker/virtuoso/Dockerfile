FROM openlink/virtuoso-opensource-7:7.2.7

RUN apt-get update && \
  apt-get install -y \
  curl

ADD enable_update.sh /enable_update.sh
ENTRYPOINT ["/bin/bash"]
CMD ["-c", "/virtuoso-entrypoint.sh start & sh /enable_update.sh & wait"]
