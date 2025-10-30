#!/bin/bash

until $(curl --output /dev/null --silent --head --fail http://virtuoso:8890); do
  echo "waiting longer..."
  sleep 1
done

sleep 1

echo "GRANT SPARQL_UPDATE to \"SPARQL\";" > grant.sql
isql -U dba -P dba virtuoso:1111 < grant.sql

echo "DONE with ISQL"
