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

# Install the d1lod python package
ADD . .
RUN pip3 install .

RUN git clone https://github.com/dajobe/redland-bindings
WORKDIR /tmp/redland-bindings

RUN sh autogen.sh
RUN ./configure --with-python=python3
RUN make install

WORKDIR /
