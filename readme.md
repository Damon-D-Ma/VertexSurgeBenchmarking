# VertexSurge VExpand & MIntersect Visualizer

**Authors:** Ziad Zananiri, Damon Ma

A Python implementation of the **VExpand** and **MIntersect** operators from the ASPLOS '24 paper *VertexSurge: Variable Length Graph Pattern Match on Billion-edge Graphs*. 
To demonstrate the inner-workings and performance benefits of VExpand and MIntersect, two scripts are provided:

1. A VertexSurge visualizer, `run_example.py`
2. A VertexSurge performance benchmarking experiment, `run_benchmark.py`

This project benchmarks highly optimized bit-matrix expansion and intersection approaches against traditional naive path-based join methods to highlight performance and memory scaling differences.

## Features

- **VExpand Visualizer:** Watch the "surge" of reachable vertices across a bit-matrix in real-time.
- **MIntersect Visualizer:** See how bitwise AND logic replaces expensive database joins to find pattern matches (like triangles).
- **Performance Benchmarking:** Compare bit-matrix logic against naive path-tracking implementations.
- **Walk Semantics:** Demonstrates why VertexSurge is "fearless" of cycles and large search depths ($k_{max}$).

## Installation

Run the following command to install the required libraries (`numpy` and `matplotlib`):

```bash
pip install -r requirements.txt
```

## How to Run

### 1. Basic Reachability Benchmark (VExpand)

Compare the time it takes to find all reachable vertices within $k$ hops.

```bash
python3 run_example.py --vertices 500 --degree 50 --kmax 5
```

### 2. Triangle Pattern Match (MIntersect)

Find all triples $(a, b, c)$ where $a \to b$, $b \to c$, and $a \to c$ exist. This demonstrates the core speedup of VertexSurge's pattern matching.

```bash
python3 run_example.py --triangle --vertices 100 --degree 5
```

### 3. Visualizer Mode

Add the `--visualize` flag to any command to see the bit-matrix operations in action.

```bash
python3 run_example.py --triangle --visualize --vertices 30 --degree 2 --kmax 3
```

### 4. Performance Benchmarking Experiment

Retrieve runtime and memory usage for Naive Extend-based joins and VertexSurge joins.
This is done with 10 randomly-generated graphs, heaving having 1000 vertices with degree 50.
```bash
python3 run_benchmark.py
```
This will produce the following:

- `memory_result.png`: peak memory usage across trials (MB)
- `runtime_result.png`: runtimes across trials (S)
- `results.txt`: a textual representation of the above information

## Command Line Arguments

- `--vertices`: Total vertices in the generated graph.
- `--degree`: Max outgoing edges per vertex.
- `--kmin`: Minimum path length/hops for the query.
- `--kmax`: Maximum path length/hops for the query.
- `--visualize`: Enable the step-by-step matplotlib visualizer.
- `--triangle`: Run the MIntersect vs. Naive Join benchmark.

---

## Interesting Test Cases

**1. The "Join Choke" (MIntersect vs. Join)**
In a moderately dense graph, traditional joins generate millions of redundant intermediate paths. MIntersect ignores paths and only tracks vertex existence, leading to massive speedups.

```bash
python3 run_example.py --triangle --vertices 200 --degree 10 --kmax 3
```

**2. The "Surge" (VExpand Visualization)**
Watch the frontier (Red) march across the matrix and leave a trail of visited vertices (Blue). If the frontier hits a previously visited node, it turns Purple (Overlap).

```bash
python3 run_example.py --vertices 20 --degree 2 --kmax 8 --visualize
```

**3. The "MIntersect Strip"**
Visualizes how two reachability rows are "AND-ed" together to find common neighbors. Look for vertical green columns in the bottom row to identify valid pattern matches.

```bash
python3 run_example.py --triangle --visualize --vertices 40 --degree 3
```
