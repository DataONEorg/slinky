#!/bin/bash

until $(curl --output /dev/null --silent --head --fail http://localhost:8890); do
  echo "waiting longer..."
  sleep 1
done

sleep 1

echo "GRANT SPARQL_UPDATE to \"SPARQL\";" > grant.sql
isql -U dba -P dba localhost:1111 < grant.sql

echo "DONE with ISQL"
