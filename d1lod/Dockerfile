FROM debian:bullseye-20210208

RUN apt-get update && \
  apt-get install -y autoconf \
  automake \ 
  git \
  librdf0-dev \
  libtool \
  python3 \
  python3-pip \
  swig

WORKDIR /tmp

RUN git clone https://github.com/dajobe/redland-bindings
WORKDIR /tmp/redland-bindings

RUN sh autogen.sh
RUN ./configure --with-python=python3
RUN make install

ADD . /tmp/d1lod
WORKDIR /tmp/d1lod

RUN python3 -m pip install -r requirements.txt
RUN python3 -m pip install pytest

CMD python3 -m pytest .
