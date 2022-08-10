# virtuoso_init

This directory contains a custom Dockerfile that lets us enable SPARQL UPDATE automatically when Virtuoso starts.

## Why Does This Exist?

We used to use [tenforce/virtuoso](https://hub.docker.com/r/tenforce/virtuoso/) but Virtuoso recommends using their [official images](https://hub.docker.com/r/openlink/virtuoso-opensource-7).
Unfortunately, the tenforce images gave us something the official images don't: The ability to run custom SQL on startup.
This includes granting SPARQL UPDATE privileges globally which is useful for running the test suite here.
