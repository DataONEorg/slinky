FROM python:3.9.13-bullseye

RUN apt-get update && \
  apt-get install -y autoconf \
  automake \
  git \
  librdf0-dev \
  libtool \
  python3 \
  python3-pip \
  swig

# Install redlands
WORKDIR /slinky
RUN wget "http://download.librdf.org/source/redland-bindings-1.0.17.1.tar.gz"
RUN tar xzvf redland-bindings-1.0.17.1.tar.gz
WORKDIR /slinky/redland-bindings-1.0.17.1
RUN sh autogen.sh
RUN ./configure --with-python=python3
RUN make install
RUN rm -r /slinky/redland-bindings-1.0.17.1

# Install the d1lod python package
ADD . .
RUN pip3 install .

WORKDIR /
