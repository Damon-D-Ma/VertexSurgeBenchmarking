#!/usr/bin/env python3

"""
NOTE: This is the script for the VertexSurge benchmarking experiment,
to run the visualizer, please use run_example.py
"""

import time
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import tracemalloc
import random

from extend_join import naive_multi_hop
from vertexsurge import vexpand


# Generate a bunch of vertices and connect them
def generate_dense_graph(num_vertices, degree):
    graph = {}
    actual_degree = min(degree, num_vertices - 1)

    for i in range(num_vertices):
        valid_targets = [n for n in range(num_vertices) if n != i]
        graph[i] = random.sample(valid_targets, actual_degree)

    return graph


# for runtime and memory benchmarking
# we run these separately because the libraries from
# either experiment could introduce some overhead
# that affects results
def measure_peak_memory(func, *args, **kwargs):
    tracemalloc.start()
    func(*args, **kwargs)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return peak / (1024 * 1024)  # MB


def measure_runtime(func, *args, **kwargs):
    t0 = time.perf_counter()
    func(*args, **kwargs)
    t1 = time.perf_counter()
    return t1 - t0


# Randomly generate a graph 10 times and check runtime + space complexity
def run_trials(num_trials=10, n=1000, d=50, kmin=1, kmax=4):
    naive_times = []
    vexp_times = []
    naive_mem = []
    vexp_mem = []
    trial_lines = []

    for i in range(num_trials):
        seed = int(time.time() * 1000) % (2**32)
        random.seed(seed)

        graph = generate_dense_graph(n, d)
        sources = list(range(min(5, n)))

        # Warmup (same as RNKG)
        _ = naive_multi_hop(graph, sources, kmin, kmax)
        _ = vexpand(graph, sources, kmin, kmax, False)

        # Runtime (separate)
        t_rel = measure_runtime(naive_multi_hop, graph, sources, kmin, kmax)
        naive_times.append(t_rel)

        t_graph = measure_runtime(vexpand, graph, sources, kmin, kmax, False)
        vexp_times.append(t_graph)

        # Memory (separate)
        mem_rel = measure_peak_memory(naive_multi_hop, graph, sources, kmin, kmax)
        naive_mem.append(mem_rel)

        mem_graph = measure_peak_memory(vexpand, graph, sources, kmin, kmax, False)
        vexp_mem.append(mem_graph)

        line = (
            f"Trial {i+1}/{num_trials}: "
            f"naive={t_rel:.5f}s ({mem_rel:.2f} MB), "
            f"vexpand={t_graph:.5f}s ({mem_graph:.2f} MB)"
        )

        print(line)
        trial_lines.append(line)

    return naive_times, vexp_times, naive_mem, vexp_mem, trial_lines


def plot_runtimes(naive_times, vexp_times):
    num_trials = len(naive_times)
    x = np.arange(num_trials)

    plt.figure(figsize=(12, 6))
    plt.bar(x, naive_times, width=0.4, label="Naive Multi-Hop", color="#4C72B0")
    plt.bar(x + 0.4, vexp_times, width=0.4, label="VExpand", color="#DD8452")

    plt.xlabel("Trial Number")
    plt.ylabel("Runtime (seconds)")
    plt.title("Runtime Per Trial (Naive Multi-Hop vs VExpand)")
    plt.xticks(x + 0.2, [f"{i+1}" for i in range(num_trials)])
    plt.legend()
    plt.grid(axis="y", linestyle="--", alpha=0.5)

    plt.savefig("runtime_results.png", dpi=200, bbox_inches="tight")
    plt.close()

    print("Runtime plot written to runtime_results.png")


def plot_memory(naive_mem, vexp_mem):
    num_trials = len(naive_mem)
    x = np.arange(num_trials)

    plt.figure(figsize=(12, 6))
    plt.bar(x, naive_mem, width=0.4, label="Naive Multi-Hop", color="#4C72B0")
    plt.bar(x + 0.4, vexp_mem, width=0.4, label="VExpand", color="#DD8452")

    plt.xlabel("Trial Number")
    plt.ylabel("Peak Memory (MB)")
    plt.title("Peak Memory Per Trial (Naive Multi-Hop vs VExpand)")
    plt.xticks(x + 0.2, [f"{i+1}" for i in range(num_trials)])
    plt.legend()
    plt.grid(axis="y", linestyle="--", alpha=0.5)

    plt.savefig("memory_results.png", dpi=200, bbox_inches="tight")
    plt.close()

    print("Memory plot written to memory_results.png")


# run experiment for 10 trials of randomly generated  graphs
# produce plots and a .txt for all the results
def main():
    naive_times, vexp_times, naive_mem, vexp_mem, trial_lines = run_trials()

    out = []
    out.append(f"Naive runtimes (S): {[round(x,5) for x in naive_times]}")
    out.append(f"VExpand runtimes (S): {[round(x,5) for x in vexp_times]}")
    out.append(f"Naive memory (MB): {[round(x,2) for x in naive_mem]}")
    out.append(f"VExpand memory (MB): {[round(x,2) for x in vexp_mem]}")

    plot_runtimes(naive_times, vexp_times)
    out.append("Runtime plot written to runtime_results.png")

    plot_memory(naive_mem, vexp_mem)
    out.append("Memory plot written to memory_results.png")

    with open("results.txt", "w") as f:
        for line in out:
            f.write(line + "\n")

if __name__ == "__main__":
    main()
