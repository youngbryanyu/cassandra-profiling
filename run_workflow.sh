#!/bin/sh

# Function to clean up docker resources
cleanup() {
    echo "Cleaning up..."
    docker rm cassandra init ycsb
    docker image rm cassandra ycsb
}

# Function to check if cassandra is ready
check_cassandra() {
    docker exec cassandra cqlsh -e "DESCRIBE KEYSPACES" > /dev/null 2>&1
}

# Process command line flags
perform_cleanup=false
while getopts "c" opt; do
  case $opt in
    c)
      perform_cleanup=true
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      exit 1
      ;;
  esac
done

# Remove the options processed by getopts
shift $((OPTIND-1))

# Validate enough command line args
if [ $# -lt 5 ]; then
    echo "Error: Not enough arguments provided."
    echo "Usage: $0 [-c] <config_name> <duration_seconds> <operation> <workload> <num_records>"
    exit 1
fi

# Get command line args
config_name=$1
duration_seconds=$2
operation=$3
workload=$4
num_records=$5

# Load .env config file (contains cassandra configuration to use)
CONFIG_FILE="./config/.env.$config_name"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: Config name must be from the options: default, lcs, lcs-rowcache, rowcache"
    echo "Error: Configuration file not found: $CONFIG_FILE"
    exit 2
fi

# Load cassandra configurations to use
echo "Loading cassandra configuration: $config_name"
export $(grep -vE '^#|^$' $CONFIG_FILE | xargs)

# Start ycsb container in background
echo "Creating ycsb container..."
docker-compose up --build -d ycsb

# Start cassandra container in background
echo "Starting cassandra in a container..."
chmod +x cql/init.sh
docker-compose up --build -d cassandra

# Wait until cassandra is ready
echo "Waint for cassandra to be ready..."
count=0
until check_cassandra; do    
    sleep 5
done
echo "Cassandra is ready!"

# Wait until ycsb container is up
echo "Waiting for ycsb container to ready..."
while [ "$(docker container inspect -f '{{.State.Status}}' "ycsb")" != "running" ]; do
    sleep 5
done
echo "ycsb container is ready!"

# Create keyspace and table using init container
echo "Populating cassandra with initial keyspace and table"
docker-compose up --build init

# Load for benchmarks
echo "Loading initial data for benchmarks..."
docker exec -it ycsb sh -c './bin/ycsb.sh load cassandra-cql -p hosts="cassandra" -p port=9042 -p recordcount='"$num_records"' -s -P ./workloads/'"$workload"''

# Run benchmarks
echo "Running benchmarks..."
docker exec ycsb sh -c './bin/ycsb.sh run cassandra-cql -p hosts="cassandra" -p port=9042 -p operationcount=2147483647 -p recordcount='"$num_records"' -p maxexecutiontime='"$duration_seconds"' -s -P ./workloads/'"$workload"' > /usr/src/ycsb/output/ycsb/'"$config_name"'.dat'

# Parse YCSB output to CSV
echo "Parsing YCSB benchmark output to CSV..."
python ./src/csv_builder.py ./output/ycsb/$config_name.dat ./output/csv/$config_name.csv 1 cassandra $workload NA NA

# Build plots
echo "Building visualization plots..."
python ./src/plot_builder.py ./output/csv/$config_name.csv $duration_seconds $workload $config_name $operation $num_records

# Stop containers
docker stop cassandra init ycsb

# Remove containers and images if -c flag set
if [ "$perform_cleanup" = true ]; then
    cleanup
fi
