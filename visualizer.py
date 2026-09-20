"""
visualizer.py

Runs an algorithm across a sweep of input sizes, plots the measured
operation counts with matplotlib, saves the PNG to disk, and returns
the base64-encoded string of that same image.
"""

import base64
import io
import os
import time

import matplotlib
matplotlib.use("Agg")  # headless backend, safe for a server process
import matplotlib.pyplot as plt

from algorithms import ALGORITHMS

# Where generated snapshots are saved locally.
SNAPSHOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "snapshots")
os.makedirs(SNAPSHOT_DIR, exist_ok=True)


def build_n_values(step: int, n_max: int):
    """0, step, 2*step, ... up to and including n_max (if it isn't
    already a multiple of step, n_max is still included as the final
    point so the chart always reaches the requested upper bound)."""
    values = list(range(0, n_max, step))
    if not values or values[-1] != n_max:
        values.append(n_max)
    if values[0] != 0:
        values.insert(0, 0)
    return sorted(set(values))


def measure(algo_key: str, step: int, n_max: int):
    """Run the algorithm at each sampled n and return (n_values, op_counts)."""
    func, display_name, big_o = ALGORITHMS[algo_key]
    n_values = build_n_values(step, n_max)

    # Recursive fibonacci explodes fast; keep the demo runnable.
    if algo_key == "fibonacci_recursive":
        n_values = [n for n in n_values if n <= 32] or [0]

    op_counts = [func(n) for n in n_values]
    return n_values, op_counts, display_name, big_o


def plot_single(algo_key: str, step: int, n_max: int):
    """Plot one algorithm's measured operation count vs n.
    Returns (png_path, base64_string, metadata_dict)."""
    n_values, op_counts, display_name, big_o = measure(algo_key, step, n_max)

    fig, ax = plt.subplots(figsize=(8, 5), dpi=120)
    ax.plot(n_values, op_counts, marker="o", linewidth=2, color="#4C72B0")
    ax.set_title(f"{display_name}  —  {big_o}")
    ax.set_xlabel("Input size (n)")
    ax.set_ylabel("Measured operations")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()

    return _finalize(fig, algo_key), _to_dict(algo_key, display_name, big_o, n_values, op_counts)


def plot_multi(algo_keys, step: int, n_max: int):
    """Plot several algorithms together on one chart for comparison.
    Returns (png_path, base64_string, metadata_dict)."""
    fig, ax = plt.subplots(figsize=(9, 6), dpi=120)
    series = {}

    for algo_key in algo_keys:
        n_values, op_counts, display_name, big_o = measure(algo_key, step, n_max)
        ax.plot(n_values, op_counts, marker="o", linewidth=2, label=f"{display_name} ({big_o})")
        series[algo_key] = _to_dict(algo_key, display_name, big_o, n_values, op_counts)

    ax.set_title("Time Complexity Comparison")
    ax.set_xlabel("Input size (n)")
    ax.set_ylabel("Measured operations")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()

    combined_key = "_".join(algo_keys)
    return _finalize(fig, combined_key), series


def _to_dict(algo_key, display_name, big_o, n_values, op_counts):
    return {
        "algo": algo_key,
        "display_name": display_name,
        "big_o": big_o,
        "n_values": n_values,
        "operation_counts": op_counts,
    }


def _finalize(fig, filename_stub: str):
    """Save the figure to disk and also return its base64 encoding."""
    timestamp = int(time.time() * 1000)
    filename = f"{filename_stub}_{timestamp}.png"
    path = os.path.join(SNAPSHOT_DIR, filename)
    fig.savefig(path, format="png")

    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode("utf-8")

    return {"path": path, "base64": encoded}
