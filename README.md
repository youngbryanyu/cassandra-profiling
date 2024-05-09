# Cassandra SCAN Performance Profiling

This program uses YCSB to run latency and throughput benchmarks of Cassandra in Docker containers. 

The results and analysis I got from running some SCAN and READ workloads are in [RESULTS.md](./RESULTS.md).

## Navigation
- [Installation and Setup](#installation-and-setup)
- [How-to-run-the-workflow](#how-to-run-the-workflow)

## Installation and Setup

### Docker
Install [docker](https://docs.docker.com/get-docker/). We use docker to run all programs inside isolated containers. Make sure docker is set up.

### YCSB
Install YCSB in the root directory of this project by running:
```
curl -O --location https://github.com/brianfrankcooper/YCSB/releases/download/0.17.0/ycsb-0.17.0.tar.gz
tar xfvz ycsb-0.17.0.tar.gz
cd ycsb-0.17.0
```

## How to run the workflow
We will run our workflow using the `run_workflow.sh` script. This script does the following: 
1. Starts a cassandra node on a docker container and sets up cassandra with the specified configurations
2. Runs the specified benchmark from a docker container
3. Processes the benchmark data and creates visualizations
4. Cleans up the container and image used.

> Note: each new benchmark for a configuration will overwrite the previous benchmark data for that configuration. On each run of the workflow script, it will attempt to make a group plot comparing data across all CSV files in the `output` directory, which creates a visualization to compare different configurations, so make sure the data files come from runs with the same, YCSB run configurations, but different cassandra configurations.

The usage of the script is:
```
./run_workflow.sh [-c] <config> <duration_seconds> <operation> <workload> <num_records> <threads>
```
where:
- `-c` is the optional flag specifying whether to cleanup and remove images and containers created by the workflow run
- `config` is one of the supported values `default`, `lcs`, `rowcache`, `lcs-rowcache`
- `duration_seconds` is the duration in seconds to run the benchmark 
- `operation` is the operation we are benchmarking using YCSB (e.g. SCAN, READ, INSERT, etc)
- `workload` is the workload we are using from YCSB (e.g. workloada, workloadb, workloadc, etc)
- `num_records` is the number of records to load for the benchmark
- `threads` is the number of threads to use for YCSB to feed operations to cassandra

All arguments are required in the order above.

The raw data from the benchmarks is written to the directory `/output/ycsb/`. The visualizations plotted from the data are located in the directory `/plots/`.
