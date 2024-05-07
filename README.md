# Cassandra SCAN Performance Profiling

This program uses YCSB to run latency and throughput benchmarks of Cassandra in Docker containers. 

## Navigation
- [Installation and Setup](#installation-and-setup)
- [How-to-run-the-workflow](#how-to-run-the-workflow)
- [SCAN profiling](#scan-profiling)
- [READ profiling](#read-profiling)

## Installation and Setup

### Docker
Install [docker](https://docs.docker.com/get-docker/) to run Cassandra nodes inside isolated containers. Make sure docker is set up.

### YCSB
Install YCSB in the root directory of this project by running:
```
curl -O --location https://github.com/brianfrankcooper/YCSB/releases/download/0.17.0/ycsb-0.17.0.tar.gz
tar xfvz ycsb-0.17.0.tar.gz
cd ycsb-0.17.0
```

## How to run the workflow
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
- `config` is one of the supported values `default`, `lcs`, `rowcache`, `lcs-rowcache`
- `duration_seconds` is the duration in seconds to run the benchmark 
- `operation` is the operation we are benchmarking using YCSB (e.g. SCAN, READ, INSERT, etc)
- `workload` is the workload we are using from YCSB (e.g. workloada, workloadb, workloadc, etc)

All arguments are required in the order above.

The raw data from the benchmarks is written to the directory `/output/ycsb`. The visualizations plotted from the data are located in the directory `/plots`.

## SCAN profiling
We compare the benchmarks of several configurations for the SCAN operation:
- Default
- Use LCS (leveled compaction strategy)
- Use row cache
- Use both LCS and row cache

For the row cache, we set the limit to 10 GB, and cache all keys and rows per partition.

Here is the setup that we use:
- 1 node cluster in Docker container
- Apache Cassandra 3.11.17 release
- 16 GB RAM

We run the benchmark on `workloade` which has a 95:5 SCAN to INSERT ratio, but set the number of operations to the max and run for 15 minutes.

### Running the benchmarks

We run the benchmark workflow for each of the 4 configurations, profiling the SCAN operation for workload e using: 
```
chmod +x run_workflow.sh
./run_workflow.sh default 900 SCAN workloade
./run_workflow.sh lcs 900 SCAN workloade
./run_workflow.sh rowcache 900 SCAN workloade
./run_workflow.sh lcs-rowcache 900 SCAN workloade
```

### Results
Below are the results comparing the latencies (mean, P95, P99) for each configuration.

![Grouped Latency Plot](./plots/read-only-do-not-modify/scan-e/latency/grouped-latency-plot.png)
![Grouped Throughput Plot](./plots/read-only-do-not-modify/scan-e/throughput/grouped-throughput-plot.png)

#### Average Latency and Throughput
We can see that the default configuration has the highest average latency and 2nd to worst throughput, which implies that it's the worst, not by any significant margin, without any specific optimizations for the usage pattern. The row cache configuration had the lowest average latency. However this result should be taken with a grain of salt since while running the workflow, I ran `node exec -it cassandra nodetool info` several times, and noticed that the rowcache has 0% utilization and 0% hit rate. Thus it appears that this is not the reason the performance improved and it may have been random.

Performance wise, all were very close.

#### P95 and P99 Latency and Throughput
Again, enabling row cache performs around the best for SCAN heavy patterns, but by a very small margin. LCS also appears to have a slight performance improvement compared to the base default configuration. The default configuration and the configuration with both enabled doesn't improve performance.

#### Discussion
The row cache in cassandra is ideal for point queries that randomly access by key, or read operations that often read the same rows. Thus, row caching is not optimized for sequential scan operations.

LCS performed slightly better that the default. But when combined with row cache, gave the worst performance which could be due to extra overhead. LCS is optimized to improve read performance by reducing the number of SSTables accessed from disk during reads. However, for scan-heavy workloads, this may not improve perfomance since scans involve reading a large volume of data sequentially.

## READ profiling
We compare the benchmarks of several configurations for the READ operation:
- Default
- Use LCS (leveled compaction strategy)
- Use row cache
- Use both LCS and row cache

For the row cache, we set the limit to 10 GB, and cache all keys and rows per partition.

Here is the setup that we use:
- 1 node cluster in Docker container
- Apache Cassandra 3.11.17 release
- 16 GB RAM

We run the benchmark on `workloadd` which has a 95:5 READ to INSERT ratio, but set the number of operations to the max and run for 15 minutes.

### Results
Below are the results comparing the latencies (mean, P95, P99) for each configuration.

#### Average Latency and Throughput

Performance wise, all were very close.

#### P95 and P99 Latency and Throughput

#### Discussion