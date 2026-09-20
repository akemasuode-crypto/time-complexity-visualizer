"""
algorithms.py

Instrumented implementations of classic algorithms.

Each function takes an integer `n` (the input size), builds suitable
sample data of that size internally, RUNS the real algorithm on it,
and returns the number of elementary operations it performed
(comparisons / array accesses / recursive calls, depending on the
algorithm). This gives an *empirically measured* operation count for
each n, rather than a theoretical formula, so the resulting plot shows
how the algorithm actually behaves.

To add a new algorithm:
  1. Write a function `def my_algo(n): ... return op_count`
  2. Register it in ALGORITHMS with a display name and Big-O label.
"""

import random


def linear_search(n: int) -> int:
    """Search for a (deliberately worst-case / absent) target in an
    unsorted list of size n. Worst case: target not present -> scans
    everything. O(n)."""
    arr = list(range(n))
    target = -1  # guaranteed not present -> worst case, full scan
    ops = 0
    for value in arr:
        ops += 1  # one comparison
        if value == target:
            break
    return ops


def binary_search(n: int) -> int:
    """Search a sorted list of size n for a value not present
    (worst case). O(log n)."""
    arr = list(range(n))
    target = -1  # not present -> forces worst-case number of halvings
    ops = 0
    lo, hi = 0, n - 1
    while lo <= hi:
        ops += 1  # one comparison
        mid = (lo + hi) // 2
        if arr[mid] == target:
            break
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return ops


def bubble_sort(n: int) -> int:
    """Sort a reverse-ordered list of size n (worst case for bubble
    sort). Counts comparisons + swaps. O(n^2)."""
    arr = list(range(n, 0, -1))  # worst case: fully reversed
    ops = 0
    for i in range(len(arr)):
        for j in range(0, len(arr) - i - 1):
            ops += 1  # comparison
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                ops += 1  # swap
    return ops


def nested_loops(n: int) -> int:
    """Canonical O(n^2) double loop, counting each inner-body
    execution as one operation."""
    ops = 0
    for i in range(n):
        for j in range(n):
            ops += 1
    return ops


# ---------------------------------------------------------------------
# Bonus algorithms
# ---------------------------------------------------------------------

def selection_sort(n: int) -> int:
    """O(n^2) — counts comparisons made while finding each minimum."""
    arr = list(range(n, 0, -1))
    ops = 0
    for i in range(len(arr)):
        min_idx = i
        for j in range(i + 1, len(arr)):
            ops += 1  # comparison
            if arr[j] < arr[min_idx]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
    return ops


def insertion_sort(n: int) -> int:
    """Worst case (reverse-sorted input). O(n^2)."""
    arr = list(range(n, 0, -1))
    ops = 0
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0:
            ops += 1  # comparison
            if arr[j] > key:
                arr[j + 1] = arr[j]
                j -= 1
            else:
                break
        arr[j + 1] = key
    return ops


def merge_sort(n: int) -> int:
    """O(n log n) — counts comparisons made during merges."""
    arr = [random.random() for _ in range(n)]
    ops = 0

    def _merge_sort(a):
        nonlocal ops
        if len(a) <= 1:
            return a
        mid = len(a) // 2
        left = _merge_sort(a[:mid])
        right = _merge_sort(a[mid:])
        merged = []
        i = j = 0
        while i < len(left) and j < len(right):
            ops += 1  # comparison
            if left[i] <= right[j]:
                merged.append(left[i]); i += 1
            else:
                merged.append(right[j]); j += 1
        merged.extend(left[i:])
        merged.extend(right[j:])
        return merged

    _merge_sort(arr)
    return ops


def quick_sort(n: int) -> int:
    """Average-case O(n log n) using a randomized pivot; counts
    comparisons against the pivot."""
    arr = [random.random() for _ in range(n)]
    ops = 0

    def _quick_sort(a):
        nonlocal ops
        if len(a) <= 1:
            return
        pivot = a[random.randrange(len(a))]
        less, equal, greater = [], [], []
        for x in a:
            ops += 1  # comparison against pivot
            if x < pivot:
                less.append(x)
            elif x > pivot:
                greater.append(x)
            else:
                equal.append(x)
        _quick_sort(less)
        _quick_sort(greater)

    _quick_sort(arr)
    return ops


def fibonacci_recursive(n: int) -> int:
    """Naive exponential-time recursive Fibonacci. O(2^n).
    Counts function calls. Capped at n<=32 to stay runnable;
    larger n values are simply skipped by the caller."""
    ops = 0

    def fib(k):
        nonlocal ops
        ops += 1  # one call
        if k <= 1:
            return k
        return fib(k - 1) + fib(k - 2)

    fib(min(n, 32))
    return ops


def constant_lookup(n: int) -> int:
    """O(1) — a single dict lookup regardless of n. Included as a
    baseline so the chart can show a flat line next to the others."""
    d = {i: i for i in range(max(n, 1))}
    ops = 0
    ops += 1  # one hash lookup, independent of n
    _ = d.get(n // 2, None)
    return ops


# Registry: internal name -> (callable, display name, Big-O label, max n allowed)
ALGORITHMS = {
    "linear_search":       (linear_search,       "Linear Search",              "O(n)"),
    "binary_search":       (binary_search,       "Binary Search",              "O(log n)"),
    "bubble_sort":         (bubble_sort,         "Bubble Sort",                "O(n^2)"),
    "nested_loops":        (nested_loops,        "Nested Loops",               "O(n^2)"),
    "selection_sort":      (selection_sort,      "Selection Sort",             "O(n^2)"),
    "insertion_sort":      (insertion_sort,      "Insertion Sort (worst case)", "O(n^2)"),
    "merge_sort":          (merge_sort,          "Merge Sort",                 "O(n log n)"),
    "quick_sort":          (quick_sort,          "Quick Sort (avg case)",      "O(n log n)"),
    "fibonacci_recursive": (fibonacci_recursive, "Recursive Fibonacci",        "O(2^n)"),
    "constant_lookup":     (constant_lookup,     "Constant-Time Lookup",       "O(1)"),
}
