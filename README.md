# Cassandra SCAN Performance Profiling

In this project, we use YCSB to run latency and throughput benchmarks of Cassandra. We compare the benchmarks of several configurations:
- Default
- Use LCS (leveled compaction strategy)
- Use row cache (10 GB)
- Use both LCS and row cache

Here is the setup that we use:
- 1 node cluster in Docker container
- Apache Cassandra 3.11.17 release
- 16 GB RAM
- scan:insert proportion= 95:5

We run the benchmark on `workloade`, but set the number of operations to the max and run for 15 minutes.

## Navigation
[Installation and Setup](#installation-and-setup)

## Installation and Setup

### Docker
Install [docker](https://docs.docker.com/get-docker/) to run Cassandra nodes inside isolated containers. Make sure docker is set up.

### YCSB
Install YCSB by running 
```
curl -O --location https://github.com/brianfrankcooper/YCSB/releases/download/0.17.0/ycsb-0.17.0.tar.gz
tar xfvz ycsb-0.17.0.tar.gz
cd ycsb-0.17.0
```

## Running the Benchmarks
We will run our workflow using the `run_workflow.sh` script. This script does the following: 
1. Starts a cassandra instance on a docker container and performs setup
2. Runs the specified benchmark
3. Processes the benchmark data and creates visualizations
4. Cleans up the container and image used.

> Note: On each run of the workflow script, it will attempt to make a group plot comparing data across all data files in the `output` directory, which aims to create a visualization to compare different configurations. Also, each new benchmark for a configuration will overwrite the previous benchmark data for that configuration.

The usage of the script is:
```
./run_workflow.sh <config> <duration_seconds> <operation> <workload>
```
where:
- `config` is one of the values `default`, `lcs`, `rowcache`, `lcs-rowcache`
- `duration_seconds` is the duration to run the benchmark 
- `operation` is the operation we are benchmarking (e.g. SCAN)
- `workload` is the workload we are using from YCSB


### Default
Run the benchmark workflow with default configurations using: 
```
chmod +x run_workflow.sh
./run_workflow.sh default 900 SCAN workloade
```

### LCS
Run the benchmark workflow with LCS enabled using:
```
chmod +x run_workflow.sh
./run_workflow.sh lcs 900 SCAN workloade 
```

### Row cache
Run the benchmark workflow with row cache enabled using:
```
chmod +x run_workflow.sh
./run_workflow.sh rowcache 900 SCAN workloade 
```

### LCS + row cache
Run the benchmark workflow with both LCS and row cache enabled using:
```
chmod +x run_workflow.sh
./run_workflow.sh lcs-rowcache 900 SCAN workloade 
```

## Results Analysis
The raw data from the benchmarks is located in the directory `/output/ycsb`. The visualizations plotted from the data are located in the directory `/plots`.

### 1 Node

Below are the comparisons of the latency metrics across the 4 configurations we tested (default, LCS, row cache, LCS + row cache)

#### Default

#### LCS

#### Row Cache

#### LCS + Row Cache