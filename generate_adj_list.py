import os
import math
import numpy as np
import json

import pickle as pkl
from collections import defaultdict
import geopandas as gpd
import osmnx as ox

from tqdm import tqdm


def angle(linestring):
    """Get angle between two end points, in radians"""
    a, b = linestring.coords[:2]
    if np.isclose(a[0], b[0]): return np.pi / 2
    return math.atan2(b[1] - a[1], b[0] - a[0])


def generate_adj_list(G):
    """
    Returns adjacency list in dictionary form.
    """
    nodes, edges = ox.graph_to_gdfs(G)
    edges = edges.rename_axis(["u", "v", "key"]).reset_index()
    edges = edges[["u", "v", "length", "geometry"]]

    adj = defaultdict(list)

    edges.reset_index()
    length_col = edges.columns.get_loc("length")
    geometry_col = edges.columns.get_loc("geometry")

    for idx, row in tqdm(list(edges.iterrows()), ncols=100):
        u, v = row["u"], row["v"]
        adj[u].append((v, row[length_col], angle(row[geometry_col])))
    
    return adj



if __name__ == "__main__":
    with open("./places.json") as fin:
        places = json.load(fin)

        for placename, slug in places:
            print(f"Creating adjacency list for {placename} (slug: {slug})")
            
            print(f"Reading graph file...")
            with open(f"./data/networks/{slug}.pkl", "rb") as fin:
                G = pkl.load(fin)
                G = ox.project_graph(G)
            nodes, edges = ox.graph_to_gdfs(G)
            
            print(f"Generating adjacency list...")
            adj = generate_adj_list(G)
            
            print(f"Saving file as json...")
            os.makedirs("./data/adj_lists", exist_ok=True)
            with open(f"./data/adj_lists/{slug}.json", "w") as fout:
                json.dump(adj, fout)

            print()
