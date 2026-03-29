#!/usr/bin/env python3

"""
NOTE: This is the script for the VertexSurge visualizer,
to run the performance benchmarking experiment, please use
run_benchmark.py
"""


from extend_join import naive_multi_hop
from vertexsurge import vexpand, mintersect
import time
import argparse
import random
import numpy as np
import time

def generate_dense_graph(num_vertices, degree):
    graph = {}
    actual_degree = min(degree, num_vertices - 1)

    for i in range(num_vertices):
        valid_targets = [n for n in range(num_vertices) if n != i]
        graph[i] = random.sample(valid_targets, actual_degree)

    return graph

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--kmin", type=int, default=1)
    parser.add_argument("--kmax", type=int, default=4)
    parser.add_argument("--vertices", type=int, default=100)
    parser.add_argument("--degree", type=int, default=5)
    parser.add_argument("--visualize", action="store_true")
    parser.add_argument("--triangle", action="store_true", help="Run triangle pattern match demo")
    return parser.parse_args()

def run_example(graph, sources, kmin, kmax, visualize):
    print("*******************************************************************************")
    print("NOTE: these examples only produce reachable destination vertices in the graph!")
    print("It DOES NOT complete the query...")
    print("*******************************************************************************")

    print(f"Graph generated with {len(graph)} vertices.")
    print(f"Running search from kmin={kmin} to kmax={kmax}...")

    print("\nTiming naive_multi_hop...")
    t0 = time.perf_counter()
    naive = naive_multi_hop(graph, sources, kmin, kmax)
    t1 = time.perf_counter()
    print("Time (elapsed):", t1 - t0)

    print("\nTiming vertexsurge/VExpand...")
    t2 = time.perf_counter()
    vexp = vexpand(graph, sources, kmin, kmax, visualize)
    t3 = time.perf_counter()
    print("Time (elapsed):", t3 - t2)

def run_triangle_example(graph, kmin, kmax, visualize):
    print("\n--- Running Triangle Pattern Match Comparison ---")
    print(f"Goal: Find (a, b, c) such that paths exist for (a,b), (b,c), and (a,c)")

    all_nodes = list(range(len(graph)))
    n = len(graph)

    print("Step 1: Preparing reachability data...")
    t_v0 = time.perf_counter()
    m = vexpand(graph, all_nodes, kmin, kmax, visualize=False)
    t_v1 = time.perf_counter()

    t_n0 = time.perf_counter()
    res_naive = naive_multi_hop(graph, all_nodes, kmin, kmax)
    t_n1 = time.perf_counter()

    print(f"VExpand built matrix in: {t_v1 - t_v0:.4f}s")
    print(f"Naive multi-hop built path-sets in: {t_n1 - t_n0:.4f}s")

    print("\nStep 2: Timing MIntersect (Bitwise Logic)...")
    from vertexsurge import mintersect
    t_m0 = time.perf_counter()
    count_m = 0

    # We iterate a and b, then use bit-magic for all c's
    for a in range(n):
        for b in range(n):
            if m[a, b]:
                c_bits = m[a] & m[b]
                # In VertexSurge C++, this is a SIMD count instruction (VPOPCNT)
                count_m += np.sum(c_bits)
    t_m1 = time.perf_counter()
    print(f"MIntersect Total Triangles: {count_m}")
    print(f"MIntersect Search Time: {t_m1 - t_m0:.4f}s")

    print("\nStep 3: Timing Naive Join (Path-based)...")
    from extend_join import naive_join
    t_j0 = time.perf_counter()
    count_j = naive_join(res_naive, res_naive, res_naive)
    t_j1 = time.perf_counter()
    print(f"Naive Join Total Triangles: {count_j}")
    print(f"Naive Join Search Time: {t_j1 - t_j0:.4f}s")

    if (t_j1 - t_j0) > 0:
        speedup = (t_j1 - t_j0) / (t_m1 - t_m0)
        print(f"\n>>> MIntersect Speedup: {speedup:.2f}x faster than Naive Join!")

    if visualize and count_m > 0:
        print("\nVisualizing one MIntersect call...")
        for a in range(n):
            for b in range(n):
                if a != b and m[a, b]:
                    mintersect(m, m, a, b, visualize=True)
                    return


if __name__ == "__main__":
    args = parse_args()

    graph = generate_dense_graph(args.vertices, args.degree)
    num_sources = min(5, args.vertices)
    sources = list(range(num_sources))

    print("\nGraph Adjacency List:")
    for node, edges in list(graph.items())[:10]:
        print(f"Node {node} -> {edges}")

    if len(graph) > 10:
        print(f"... and {len(graph) - 10} more nodes")
    print("\n")

    if args.triangle:
        run_triangle_example(graph, args.kmin, args.kmax, args.visualize)
    else:
        run_example(graph, sources, args.kmin, args.kmax, args.visualize)
