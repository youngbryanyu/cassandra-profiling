# Use official cassandra image as base
FROM cassandra:3.11.17

# Define config environment variables
ARG CONFIG_PATH
ARG CQL_PATH

# Copy custom config file 
COPY ${CONFIG_PATH} /etc/cassandra/cassandra.yaml

# Copy CQL init scripts
COPY ${CQL_PATH} /init.cql 

# Expose ports
EXPOSE 9042

# Set run command 
CMD ["cassandra", "-f"]

