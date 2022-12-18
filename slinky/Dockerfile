FROM python:3.9.13-bullseye

RUN apt-get update && \
  apt-get install -y autoconf \
  automake \
  git \
  librdf0-dev \
  libtool \
  swig \
  && rm -rf /var/lib/apt/lists/*

# Install redlands
WORKDIR /slinky
RUN wget "http://download.librdf.org/source/redland-bindings-1.0.17.1.tar.gz"
RUN tar xzvf redland-bindings-1.0.17.1.tar.gz
WORKDIR /slinky/redland-bindings-1.0.17.1
RUN sh autogen.sh && ./configure --with-python=python3 && make install
# Remove redland artifacts
WORKDIR /slinky
RUN rm -r redland-bindings-1.0.17.1 && rm redland-bindings-1.0.17.1.tar.gz

# Create the slinky user
RUN useradd -ms /bin/bash slinky
USER slinky
ENV PATH="/home/slinky/.local/bin:${PATH}"
WORKDIR /home/slinky

# Copy the slinky source and install
ADD --chown=slinky:slinky . .
RUN python -m pip install -U pip && pip install . --user
