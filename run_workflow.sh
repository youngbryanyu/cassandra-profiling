#!/bin/sh

# Function to clean up docker resources
cleanup() {
    echo "Cleaning up..."
    docker stop cassandra init
    docker rm cassandra init
    docker image rm cassandra
}

# Function to check if cassandra is ready
check_cassandra() {
    docker exec cassandra cqlsh -e "DESCRIBE KEYSPACES" > /dev/null 2>&1
}

# Validate enough command line args
if [ $# -lt 4 ]; then
    echo "Error: Not enough arguments provided."
    echo "Usage: $0 <config_name> <duration_seconds> <operation> <workload>"
    exit 1
fi

# Load .env config file (contains cassandra configuration to use)
CONFIG_FILE="./config/.env.$1"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: Config name must be from the options: default, lcs, lcs-rowcache, rowcache"
    echo "Error: Configuration file not found: $CONFIG_FILE"
    exit 2
fi

# Load the configurations
echo "Loading cassandra configuration: $1"
export $(grep -vE '^#|^$' $CONFIG_FILE | xargs)

# Start cassandra in docker container
echo "Starting cassandra image in a container..."
chmod +x cql/init.sh
docker-compose up --build -d cassandra

# Wait until cassandra is ready or until it times out
MAX_TRIES=30
SLEEP_SECONDS=10
count=0
until check_cassandra; do
    count=$((count+1))
    checks_left=$((MAX_TRIES - count))
    
    if [ $count -ge $MAX_TRIES ]; then
        echo "Cassandra is not up after $MAX_TRIES attempts, stopping..."
        cleanup
        exit 1
    fi
    echo "Cassandra not ready yet, checking again in $SLEEP_SECONDS seconds... ($checks_left checks left until timeout)"
    sleep $SLEEP_SECONDS
done
echo "Cassandra is ready!"

# Create keyspace and table
echo "Populating cassandra with initial keyspace and table"
docker-compose up --build -d init

# Run benchmarks
echo "Running benchmarks..."
./ycsb/bin/ycsb.sh run cassandra-cql -p hosts="localhost" -p port=9042 -p operationcount=2147483647 -p maxexecutiontime=$2 -s -P ycsb/workloads/$4 > output/ycsb/$1.dat

# Parse YCSB output to CSV
echo "Parsing YCSB benchmark output to CSV..."
python ./src/csv_builder.py ./output/ycsb/$1.dat ./output/csv/$1.csv 1 cassandra $4 NA NA

# Build plots
echo "Building visualization plots..."
python ./src/plot_builder.py ./output/csv/$1.csv $2 $4 $1 $3

# Cleanup
cleanup
