"""
app.py

Flask server for the Time Complexity Visualizer.

Endpoint
--------
GET /analyze?algo=<name[,name2,...]>&step=<int>&n_max=<int>

Query params
------------
algo   : one algorithm name, or a comma-separated list of names, from
         the supported set (see /algorithms for the full list).
         Brackets/quotes are tolerated and stripped, e.g. both
         `algo=linear_search` and `algo=['linear_search']` work.
step   : positive integer increment between sampled input sizes.
n_max  : maximum input size to test. The minimum is always 0.
         Commas are tolerated, e.g. `n_max=10,000`.

Example
-------
  http://localhost:8000/analyze?algo=linear_search&step=10&n_max=10000
  http://localhost:8000/analyze?algo=linear_search,bubble_sort&step=50&n_max=1000

Response JSON
-------------
{
  "algo": "linear_search",
  "step": 10,
  "n_max": 10000,
  "min_n": 0,
  "results": { ... per-algorithm n_values / operation_counts / big_o ... },
  "image_base64": "<base64 PNG>",
  "image_path": "/absolute/path/to/saved/snapshot.png"
}
"""

import re

from flask import Flask, jsonify, request

from algorithms import ALGORITHMS
from visualizer import plot_multi, plot_single

app = Flask(__name__)


def _clean_int(raw: str) -> int:
    """Parse an integer query param, tolerating thousands separators
    like '10,000' and stray whitespace."""
    cleaned = raw.replace(",", "").strip()
    return int(cleaned)


def _clean_algo_list(raw: str):
    """Parse the algo query param into a list of algorithm keys.
    Tolerates surrounding brackets/quotes, e.g. "['linear_search']",
    and comma-separated lists, e.g. "linear_search,bubble_sort"."""
    stripped = re.sub(r"[\[\]'\"]", "", raw)
    keys = [k.strip() for k in stripped.split(",") if k.strip()]
    return keys


@app.route("/algorithms", methods=["GET"])
def list_algorithms():
    """Convenience endpoint listing every supported algorithm."""
    return jsonify({
        key: {"display_name": name, "big_o": big_o}
        for key, (_, name, big_o) in ALGORITHMS.items()
    })


@app.route("/analyze", methods=["GET"])
def analyze():
    algo_raw = request.args.get("algo")
    step_raw = request.args.get("step")
    n_max_raw = request.args.get("n_max")

    if not algo_raw or not step_raw or not n_max_raw:
        return jsonify({
            "error": "Missing required query parameters. Required: algo, step, n_max.",
            "example": "/analyze?algo=linear_search&step=10&n_max=10000",
        }), 400

    algo_keys = _clean_algo_list(algo_raw)
    unknown = [k for k in algo_keys if k not in ALGORITHMS]
    if unknown or not algo_keys:
        return jsonify({
            "error": f"Unknown algorithm(s): {unknown}" if unknown else "No algorithm provided.",
            "supported_algorithms": sorted(ALGORITHMS.keys()),
        }), 400

    try:
        step = _clean_int(step_raw)
        n_max = _clean_int(n_max_raw)
    except ValueError:
        return jsonify({"error": "step and n_max must be integers."}), 400

    if step <= 0:
        return jsonify({"error": "step must be a positive integer."}), 400
    if n_max < 0:
        return jsonify({"error": "n_max must be >= 0 (minimum n is always 0)."}), 400

    if len(algo_keys) == 1:
        image, results = plot_single(algo_keys[0], step, n_max)
        response = {
            "algo": algo_keys[0],
            "step": step,
            "n_max": n_max,
            "min_n": 0,
            "results": results,
            "image_base64": image["base64"],
            "image_path": image["path"],
        }
    else:
        image, results = plot_multi(algo_keys, step, n_max)
        response = {
            "algo": algo_keys,
            "step": step,
            "n_max": n_max,
            "min_n": 0,
            "results": results,
            "image_base64": image["base64"],
            "image_path": image["path"],
        }

    return jsonify(response), 200


@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "service": "Time Complexity Visualizer",
        "endpoints": {
            "/analyze": "GET - analyze algorithm(s); params: algo, step, n_max",
            "/algorithms": "GET - list supported algorithms",
        },
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)
