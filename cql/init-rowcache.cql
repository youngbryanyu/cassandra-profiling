-- Create the keyspace
CREATE KEYSPACE ycsb WITH REPLICATION = {'class' : 'SimpleStrategy', 'replication_factor' : 3};

-- Use the keyspace
USE ycsb;

-- Create the table
CREATE TABLE usertable (
    y_id varchar PRIMARY KEY,
    field0 varchar,
    field1 varchar,
    field2 varchar,
    field3 varchar,
    field4 varchar,
    field5 varchar,
    field6 varchar,
    field7 varchar,
    field8 varchar,
    field9 varchar
) WITH caching = {'keys': 'NONE', 'rows_per_partition': 'ALL'};
