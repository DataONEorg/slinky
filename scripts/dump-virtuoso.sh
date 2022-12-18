#!/bin/sh

# Runs http://vos.openlinksw.com/owiki/wiki/VOS/VirtRDFDumpNQuad

set -e

# Name of the Virtuosos container
CONTAINER=$(docker ps --format "{{.Names}}" | grep virtuoso)
# Location where Virtuoso puts the nq files
DUMP_DIR="/opt/virtuoso-opensource/database/dumps/"

if [ -z "$CONTAINER" ]; then
  echo "Didn't find a running virtuoso container. Exiting."
  exit;
fi

# Virtuoso expects a folder named 'dumps'
docker exec -i "$CONTAINER" mkdir "$DUMP_DIR"

# Add the dump_nquads method
docker exec -i "$CONTAINER" isql <<EOF
  CREATE PROCEDURE dump_nquads 
  ( IN  dir                VARCHAR := 'dumps'
  , IN  start_from             INT := 1
  , IN  file_length_limit  INTEGER := 100000000
  , IN  comp                   INT := 1
  )
  {
    DECLARE  inx, ses_len  INT
  ; DECLARE  file_name     VARCHAR
  ; DECLARE  env, ses      ANY
  ;

  inx := start_from;
  SET isolation = 'uncommitted';
  env := vector (0,0,0);
  ses := string_output (10000000);
  FOR (SELECT * FROM (sparql define input:storage "" SELECT ?s ?p ?o ?g { GRAPH ?g { ?s ?p ?o } . FILTER ( ?g != virtrdf: ) } ) AS sub OPTION (loop)) DO
    {
      DECLARE EXIT HANDLER FOR SQLSTATE '22023' 
	{
	  GOTO next;
	};
      http_nquad (env, "s", "p", "o", "g", ses);
      ses_len := LENGTH (ses);
      IF (ses_len >= file_length_limit)
	{
	  file_name := sprintf ('%s/output%06d.nq', dir, inx);
	  string_to_file (file_name, ses, -2);
	  IF (comp)
	    {
	      gz_compress_file (file_name, file_name||'.gz');
	      file_delete (file_name);
	    }
	  inx := inx + 1;
	  env := vector (0,0,0);
	  ses := string_output (10000000);
	}
      next:;
    }
  IF (length (ses))
    {
      file_name := sprintf ('%s/output%06d.nq', dir, inx);
      string_to_file (file_name, ses, -2);
      IF (comp)
	{
	  gz_compress_file (file_name, file_name||'.gz');
	  file_delete (file_name);
	}
      inx := inx + 1;
      env := vector (0,0,0);
    }
}; 
exit;
EOF

# Create the dumps
docker exec -i "$CONTAINER" isql <<EOF
  dump_nquads ('dumps', 1, 10000000, 1);
    exit;
EOF

# Copy the dumps out of the container
docker cp "$CONTAINER":"$DUMP_DIR" ./data
