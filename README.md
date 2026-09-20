# Time Complexity Visualizer

A small Flask service that empirically measures how many operations an
algorithm actually performs as its input size `n` grows, plots the
result with matplotlib, and returns the chart as both a saved PNG and
a base64-encoded string in the JSON response.

Rather than plotting a theoretical formula, each algorithm is
instrumented — the real code runs on real (worst-case, where
applicable) input at every sampled `n`, and every comparison / swap /
call is counted.

## Requirements

- Python 3.9+
- `pip install -r requirements.txt`

## Running the server

```bash
pip install -r requirements.txt
python app.py
```

The server listens on **http://localhost:8000**.

## API

### `GET /analyze`

| Param   | Required | Description                                                                 |
|---------|----------|-------------------------------------------------------------------------------|
| `algo`  | yes      | Algorithm name, or a comma-separated list of names (see `/algorithms`).      |
| `step`  | yes      | Positive integer increment between sampled input sizes.                      |
| `n_max` | yes      | Maximum input size to test. Minimum is always assumed to be `0`.             |

`algo` and `n_max` tolerate a bit of messiness: surrounding brackets/quotes
(`['linear_search']`) and thousands separators (`10,000`) are both stripped
automatically.

**Single algorithm:**

```
http://localhost:8000/analyze?algo=linear_search&step=10&n_max=10000
```

**Multiple algorithms on one comparison chart:**

```
http://localhost:8000/analyze?algo=bubble_sort,binary_search,nested_loops&step=50&n_max=1000
```

**Response shape (single algorithm):**

```json
{
  "algo": "linear_search",
  "step": 10,
  "n_max": 10000,
  "min_n": 0,
  "results": {
    "algo": "linear_search",
    "display_name": "Linear Search",
    "big_o": "O(n)",
    "n_values": [0, 10, 20, "...", 10000],
    "operation_counts": [0, 10, 20, "...", 10000]
  },
  "image_base64": "iVBORw0KGgoAAAANSUhEUgAA...",
  "image_path": "/absolute/path/to/time_complexity_visualizer/snapshots/linear_search_<timestamp>.png"
}
```

For multiple algorithms, `algo` is a list and `results` is a dict keyed by
algorithm name, each with the same `display_name` / `big_o` / `n_values` /
`operation_counts` shape; the returned image overlays every requested
algorithm on one chart.

Every generated chart is also saved to disk under `snapshots/` as a
timestamped PNG, in addition to being returned as base64.

### `GET /algorithms`

Lists every supported algorithm with its display name and Big-O class.

## Supported algorithms

| Key                    | Complexity   | Notes                                          |
|-------------------------|-------------|-------------------------------------------------|
| `linear_search`          | O(n)        | Required                                        |
| `binary_search`          | O(log n)    | Required                                        |
| `bubble_sort`            | O(n^2)      | Required                                        |
| `nested_loops`           | O(n^2)      | Required                                        |
| `selection_sort`         | O(n^2)      | Bonus                                           |
| `insertion_sort`         | O(n^2)      | Bonus (worst-case, reverse-sorted input)        |
| `merge_sort`             | O(n log n)  | Bonus                                           |
| `quick_sort`             | O(n log n)  | Bonus (randomized pivot, average case)          |
| `fibonacci_recursive`    | O(2^n)      | Bonus (capped at n=32 to stay runnable)         |
| `constant_lookup`        | O(1)        | Bonus (flat baseline for comparison)            |

## Project structure

```
.
├── app.py            # Flask server / routes / query-param parsing
├── algorithms.py      # Instrumented algorithm implementations + registry
├── visualizer.py       # Runs the sweep, builds the matplotlib chart, base64-encodes it
├── requirements.txt
├── snapshots/          # PNG charts saved on every /analyze call (gitignored contents)
└── README.md
```

## Error handling

- Missing `algo`, `step`, or `n_max` → `400` with a usage example.
- Unknown algorithm name → `400` listing supported algorithms.
- Non-integer `step`/`n_max`, non-positive `step`, or negative `n_max` → `400`.
