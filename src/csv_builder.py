import re
import sys
import csv


# Parses .dat logs from YCSB benchmarks into CSV format for easy plotting
def parse_log_to_csv(logfile, csvfile, runid, db, workload, threads, records):
    with open(logfile) as f:
        data = []
        data.append(
            ["RUNID", "DB", "WORKLOAD", "THREADS", "RECORDS", "OP", "METRIC", "VALUE"]
        )  # Header row

        # Parse lines that match the format
        for line in f:
            line = line.rstrip()
            if re.search(
                r"^\[OVERALL\]|^\[SCAN\]|^\[INSERT\]|^\[UPDATE\]|^\[DELETE\]|^\[READ\]",
                line,
            ):
                parts = line.split(",")
                data.append(
                    [
                        runid,
                        db,
                        workload,
                        threads,
                        records,
                        parts[0].strip(),  # OP
                        parts[1].strip(),  # METRIC
                        parts[2].strip(),  # VALUE
                    ]
                )

        # Write CSV to file
        with open(csvfile, "w", newline="") as fout:
            writer = csv.writer(fout)
            writer.writerows(data)

# Entry point
if __name__ == "__main__":
    if len(sys.argv) < 8:
        print(
            "Usage: python3 csv_builder.py <log_file> <csv_file> <run_id> <db> <workload> <threads> <records>"
        )
        sys.exit(1)
    parse_log_to_csv(*sys.argv[1:])
