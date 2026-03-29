#!/usr/bin/env python3

import time
from collections import defaultdict

"""
The extend operator that a traditional multi-hop query would use (naive).

Finds candidiates for the next hop given the current paths and the graph
"""
def extend(paths, graph):
    res = []
    for (src, dst) in paths:
        for next in graph[dst]:
            res.append((src, next))
    return res


"""
Example code for a standard naive extend + join operation for variable-
length graph database patterns
"""
def naive_multi_hop(graph, sources, kmin, kmax):
    paths = [(s, s) for s in sources]
    res = defaultdict(set)
    start_time = time.time()

    for k in range(1, kmax + 1):
        if time.time() - start_time > 10.0:
            print(f">>> [TIMEOUT] naive_multi_hop exceeded 10s at k={k}. Returning partial results.")
            break
            
        paths = extend(paths, graph)
        if k >= kmin:
            for src, dst in paths:
                res[src].add(dst)
    return res

def naive_join(res_ab, res_bc, res_ac):
    """
    Simulates a traditional join-based pattern match for a triangle.
    Joins (a,b) with (b,c) and then filters by (a,c).
    Returns the total count of (a,b,c) triangles found.
    """
    count = 0
    for a in res_ab:
        for b in res_ab[a]:
            if b in res_bc:
                for c in res_bc[b]:
                    if c in res_ac.get(a, set()):
                        count += 1
    return count
