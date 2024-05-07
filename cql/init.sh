#!/bin/sh
set -e

# Run CQL to create keyspaces and tables for YCSB.
# The proper init.cql depending on the config is copied into the image.
cqlsh cassandra 9042 -f /init.cql