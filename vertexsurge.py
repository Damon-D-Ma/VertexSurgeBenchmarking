#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

# we visualize 'res' (accumulated results) in Blue and 'frontier' (current surge) in Red
my_cmap = ListedColormap(['white', 'blue', 'red', 'purple'])

"""
Simple example for the VExpand operator (used by VertexSurge)
Returns a |S|*|V| boolean matrix of reachable 
"""
def vexpand(graph, sources, kmin, kmax, visualize=True):
    n = len(graph)
    S = list(sources)
    idx = {s: i for i, s in enumerate(S)}

    # now we make the bit-matrix, where rows are source nodes, 
    # and columns are destination vertices
    frontier = np.zeros((len(S), n), dtype=bool)

    # setup the frontier
    for s in S:
        frontier[idx[s], s] = True
    
    res = np.zeros((len(S), n), dtype=bool)

    if visualize:
        plt.ion()
        fig, ax = plt.subplots(figsize=(10, 5))

    for k in range(1, kmax + 1):
        new_frontier = np.zeros_like(frontier)

        # now we do a multi-source expansion
        for v in range(n):
            if frontier[:, v].any():
                for next_node in graph[v]:
                    new_frontier[:, next_node] |= frontier[:, v] # <--- THE BITEWISE OR TRICK (SIMD in C++)
        
        frontier = new_frontier
        
        # --- VISUALIZATION BLOCK ---
        if visualize:
            ax.clear()
            # we visualize 'res' (accumulated results) in Blue and 'frontier' (current surge) in Red
            # combining them for display: 0=None, 1=Result, 2=Frontier, 3=Both (Overlap)
            display_matrix = res.astype(int) + (frontier.astype(int) * 2)
            
            ax.imshow(display_matrix, cmap=my_cmap, vmin=0, vmax=3, aspect='auto')
            
            # grid and labels
            ax.set_xticks(range(n))
            ax.set_yticks(range(len(S)))
            ax.set_yticklabels(S)
            ax.set_xlabel(f"Graph Vertex IDs (0 to {n-1})")
            ax.set_ylabel("Source Node IDs")
            ax.set_title(f"VertexSurge VExpand - Step {k}/{kmax}\n(Red=Frontier, Blue=Visited, Purple=Overlap)")
            ax.grid(which='major', color='black', linestyle='-', linewidth=0.5)
            
            plt.draw()
            plt.pause(1.0) # pause for 1 second to view the step
        # ---------------------------

        if k >= kmin:
            res |= frontier

    if visualize:
        plt.ioff()
        plt.pause(10.0)
    
    return res

"""
The MIntersect operator (used by VertexSurge for pattern matching)
Intersects two 'edge lists' (rows in our bit-matrix) to find matches for a third vertex.
Example: for a triangle (a,b,c), it finds 'c' such that (a,c) and (b,c) exist.
"""
def mintersect(m1, m2, row1, row2, visualize=True):
    n = m1.shape[1]
    res = m1[row1] & m2[row2]
    
    if visualize:
        plt.ion()
        fig, ax = plt.subplots(figsize=(10, 4))
        
        # We show three rows:
        # Row 0: Reachable from 'a'
        # Row 1: Reachable from 'b'
        # Row 2: Result (reachable from both)
        display_matrix = np.zeros((3, n), dtype=int)
        display_matrix[0] = m1[row1].astype(int)
        display_matrix[1] = m2[row2].astype(int)
        display_matrix[2] = res.astype(int)
        
        intersect_cmap = ListedColormap(['white', 'green'])
        ax.imshow(display_matrix, cmap=intersect_cmap, vmin=0, vmax=1, aspect='auto')
        
        ax.set_yticks([0, 1, 2])
        ax.set_yticklabels(['A -> C candidates', 'B -> C candidates', 'MIntersect (C matches)'])
        ax.set_xlabel("Vertex ID (for potential 'c' nodes)")
        ax.set_title(f"VertexSurge MIntersect - Pattern Expansion\n(Green = Possible Match)")
        ax.grid(which='major', color='black', linestyle='-', linewidth=0.5)
        
        plt.draw()
        plt.pause(20.0)
        plt.ioff()
    
    return res
