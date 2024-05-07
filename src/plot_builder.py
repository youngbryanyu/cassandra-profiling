import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys
import os


# Plots the throughput of a single configuration
def plot_latency(
    csv_path,
    duration_seconds,
    workload,
    configuration,
    operation,
    output_dir="plots/latency",
):
    # Check if output directory exists and create if not
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Get dataframe of the target operations
    df = pd.read_csv(csv_path)
    scan_df = df[df["OP"].str.contains(operation)]

    # Collect metrics and their labels
    metrics = [
        "AverageLatency(us)",
        "MinLatency(us)",
        "MaxLatency(us)",
        "95thPercentileLatency(us)",
        "99thPercentileLatency(us)",
    ]
    latency_values = []
    labels = []
    for metric in metrics:
        if metric in scan_df["METRIC"].values:
            value = scan_df[scan_df["METRIC"] == metric]["VALUE"].astype(float).mean()
            latency_values.append(value)
            labels.append(metric[: -len("Latency(us)")].rstrip())

    # Build histogram
    plt.figure(figsize=(10, 6))
    bars = plt.bar(labels, latency_values, color="skyblue")
    for bar in bars:
        yval = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            yval,
            round(yval, 2),
            ha="center",
            va="bottom",
            fontsize=10,
            color="black",
        )

    # Label plot
    plt.xlabel("Metrics", fontsize=12, fontweight="bold")
    plt.ylabel("Latency (us)", fontsize=12, fontweight="bold")
    plt.title(
        f"{operation} Latency Metrics ({workload}, {float(duration_seconds)/60:.2f} minutes)",
        fontsize=14,
        fontweight="bold",
    )
    plt.grid(True)

    # Save plot
    plot_filename = os.path.join(output_dir, f"{configuration}-latency-plot.png")
    plt.savefig(plot_filename)
    plt.close()


# Plots the throughput of a single configuration
def plot_throughput(
    csv_path,
    duration_seconds,
    workload,
    configuration,
    operation,
    output_dir="plots/throughput",
):
    # Create output dir if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Get dataframe of the target operation
    df = pd.read_csv(csv_path)
    operation_df = df[df["OP"].str.contains(operation)]

    # Collect metrics and their labels
    metrics = ["Operations"]
    throughput_values = []
    labels = []
    for metric in metrics:
        if metric in operation_df["METRIC"].values:
            value = (
                operation_df[operation_df["METRIC"] == metric]["VALUE"]
                .astype(float)
                .mean()
            )
            throughput_values.append(value)
            labels.append(metric.rstrip())

    # Build histogram
    plt.figure(figsize=(10, 6))
    bars = plt.bar(labels, throughput_values, color="skyblue")
    for bar in bars:
        yval = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            yval,
            round(yval, 2),
            ha="center",
            va="bottom",
            fontsize=10,
            color="black",
        )

    # Label plot
    plt.xlabel("Metrics", fontsize=12, fontweight="bold")
    plt.ylabel("Throughput (operations)", fontsize=12, fontweight="bold")
    plt.title(
        f"{operation} Throughput Metrics ({workload}, {float(duration_seconds)/60:.2f} minutes)",
        fontsize=14,
        fontweight="bold",
    )
    plt.grid(True)

    # Save plot
    plot_filename = os.path.join(output_dir, f"{configuration}-throughput-plot.png")
    plt.savefig(plot_filename)
    plt.close()


# Plots the latency of all configurations for which there is data
def plot_grouped_latency(
    duration_seconds,
    workload,
    operation,
    directory="output/csv",
    output_dir="plots/latency",
):
    # Check if output directory exists and create if not
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Prepare data storage structure
    metrics = [
        "AverageLatency(us)",
        "95thPercentileLatency(us)",
        "99thPercentileLatency(us)",
    ]
    data = {metric: [] for metric in metrics}
    files = []

    # Collect metrics and their labels for each configuration's CSV data
    for filename in os.listdir(directory):
        if filename.endswith(".csv"):
            files.append(filename[:-4])
            csv_path = os.path.join(directory, filename)
            df = pd.read_csv(csv_path)
            scan_df = df[df["OP"].str.contains(operation)]

            # Parse data for each metric
            for metric in metrics:
                if metric in scan_df["METRIC"].values:
                    value = (
                        scan_df[scan_df["METRIC"] == metric]["VALUE"]
                        .astype(float)
                        .mean()
                    )
                    data[metric].append(value)
                else:
                    data[metric].append(0)  # Append 0 if metric not found

    # Get number of metric groups and number of bars in each group
    n_groups = len(metrics)
    n_bars = len(files)

    # Set up plot
    fig, ax = plt.subplots(figsize=(12, 8))
    index = np.arange(n_groups)
    bar_width = 0.15
    opacity = 0.8

    # Create bars for each file
    for i in range(n_bars):
        means = [data[metric][i] for metric in metrics]
        bars = plt.bar(
            index + i * bar_width, means, bar_width, alpha=opacity, label=files[i]
        )

        # Add value labels above each bar
        for bar, mean in zip(bars, means):
            ax.annotate(
                f"{round(mean, 2)}",
                xy=(bar.get_x() + bar.get_width() / 2, mean),
                xytext=(0, 3),  # 3 points vertical offset
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=9,
                color="black",
                rotation=30,
            )

    # Add labels, title, and custom x-axis tick labels, etc.
    ax.set_xlabel("Metric", fontsize=12, fontweight="bold")
    ax.set_ylabel("Latency (us)", fontsize=12, fontweight="bold")
    ax.set_title(
        f"{operation} Latency Metrics by Configuration ({workload}, {float(duration_seconds)/60:.2f} minutes)",
        fontsize=14,
        fontweight="bold",
    )
    ax.set_xticks(index + bar_width * (n_bars - 1) / 2)
    ax.set_xticklabels(metrics, fontsize=10)
    ax.legend()

    plt.tight_layout()
    plt.grid(True)

    # Save plot
    plot_filename = os.path.join(output_dir, "grouped-latency-plot.png")
    plt.savefig(plot_filename)
    plt.close()


# Plots the throughput of all configurations for which there is data
def plot_grouped_throughput(
    duration_seconds,
    workload,
    operation,
    directory="output/csv",
    output_dir="plots/throughput",
):
    # Check if output directory exists and create if not
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Prepare data storage structure
    metrics = ["Operations"]
    data = {metric: [] for metric in metrics}
    files = []

    # Collect metrics and their labels for each configuration's CSV data
    for filename in os.listdir(directory):
        if filename.endswith(".csv"):
            files.append(filename[:-4])  # Store filename without extension
            csv_path = os.path.join(directory, filename)
            df = pd.read_csv(csv_path)
            scan_df = df[df["OP"].str.contains(operation)]

            # Parse data for each metric
            for metric in metrics:
                if metric in scan_df["METRIC"].values:
                    value = (
                        scan_df[scan_df["METRIC"] == metric]["VALUE"]
                        .astype(float)
                        .mean()
                    )
                    data[metric].append(value)
                else:
                    data[metric].append(0)  # Append 0 if metric not found

    # Get number of metric groups and number of bars in each group
    n_groups = len(metrics)
    n_bars = len(files)

    # Set up plot
    fig, ax = plt.subplots(figsize=(12, 8))
    index = np.arange(n_groups)
    bar_width = 0.15
    opacity = 0.8

    # Create bars for each file
    for i in range(n_bars):
        means = [data[metric][i] for metric in metrics]
        bars = plt.bar(
            index + i * bar_width, means, bar_width, alpha=opacity, label=files[i]
        )

        # Add value labels above each bar
        for bar, mean in zip(bars, means):
            ax.annotate(
                f"{round(mean, 2)}",
                xy=(bar.get_x() + bar.get_width() / 2, mean),
                xytext=(0, 3),  # 3 points vertical offset
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=9,
                color="black",
                rotation=30,
            )

    # Add labels, title, and custom x-axis tick labels, etc.
    ax.set_xlabel("Metric", fontsize=12, fontweight="bold")
    ax.set_ylabel("Throughput (operations)", fontsize=12, fontweight="bold")
    ax.set_title(
        f"{operation} Throughput Metrics by Configuration ({workload}, {float(duration_seconds)/60:.2f} minutes)",
        fontsize=14,
        fontweight="bold",
    )
    ax.set_xticks(index + bar_width * (n_bars - 1) / 2)
    ax.set_xticklabels(metrics, fontsize=10)
    ax.legend()

    plt.tight_layout()
    plt.grid(True)

    # Save plot
    plot_filename = os.path.join(output_dir, "grouped-throughput-plot.png")
    plt.savefig(plot_filename)
    plt.close()


# Entry point
if __name__ == "__main__":
    if len(sys.argv) < 5:
        print(
            "Usage: python3 throughput.py <csv_file> <duration_seconds> <workload> <configuration> <operation>"
        )
        sys.exit(1)

    plot_latency(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    plot_throughput(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    plot_grouped_latency(sys.argv[2], sys.argv[3], sys.argv[5])
    plot_grouped_throughput(sys.argv[2], sys.argv[3], sys.argv[5])
    
