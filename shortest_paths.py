# Determine shortest time to boba for each starting point.
# This is multiple-source shortest-path problem.

import os
from heapq import heappush, heappop
import json
import pickle

from data import get_data
from random_walks import get_end_nodes

def shortest_paths(adj, end_nodes):
    """
    Return a dict of {node: shortest_time}.
    """
    costs = {}
    q = [(0, node) for node in end_nodes]
    while len(q) > 0:
        cost, node = heappop(q)
        if node in costs: continue
        costs[node] = cost

        for nbr, length, _, _ in adj[node]:
            if nbr in costs: continue
            heappush(q, (cost + length / 4 / 1000 * 60, nbr))
    
    return costs


if __name__ == "__main__":
    with open("./places.json") as fin:
        places = json.load(fin)
    
    for placename, coords, slug in places:
        print(f"Calculating shortest paths for {placename} (slug: {placename})")

        G, adj, boba_gdf = get_data(slug)
        end_nodes = get_end_nodes(G, boba_gdf)

        costs = shortest_paths(adj, end_nodes)
        
        print(f"Done. Saving...")

        os.makedirs("./data/shortest_paths", exist_ok=True)
        with open(f"./data/shortest_paths/{slug}.pkl", "wb") as fout:
            pickle.dump(costs, fout)

        print()
