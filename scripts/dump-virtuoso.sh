#!/bin/sh

# Runs http://vos.openlinksw.com/owiki/wiki/VOS/VirtRDFDumpNQuad

set -e

CONTAINER=$(docker ps --format "{{.Names}}" | grep virtuoso)

if [ -z "$CONTAINER" ]; then
  echo "Didn't find a running virtuoso container. Exiting."
  exit;
fi

docker exec -i "$CONTAINER" isql-v <<EOF
  dump_nquads ('dumps', 1, 10000000, 1);
    exit;
EOF
