import random
import numpy as np

import json
import pickle
import geopandas as gpd
import osmnx as ox

def get_end_nodes(G, boba_gdf):
    """
    Return a dict mapping "end nodes" to nodes with boba.
    """
    end_nodes = {}
    nodes = ox.nearest_nodes(G, boba_gdf["geometry"].x, boba_gdf["geometry"].y)

    for i, node in enumerate(nodes):
        shop_id = boba_gdf.iloc[i]["id"]
        end_nodes[node] = shop_id
        for edge in G.in_edges(node):
            end_nodes[edge[0]] = shop_id

    return end_nodes


def angle_diff(a, b):
    diff = a - b
    if diff < -np.pi/2: return diff + np.pi
    if diff > np.pi/2: return diff - np.pi
    return diff

# Keep visiting nodes till we hit something in end_nodes
def random_walk(adj, end_nodes, start, timeout=60*2.5):
    """
    Do a random walk starting from node <start> (node id)
        until we hit a boba shop, hit a dead end, or time out.

    Timeout is in seconds. If we haven't reached a boba shop or
        a dead end by that time, we terminate.
    
    Returns an ordered tuple:
        [0] route:        list of tuples (node id, time)
        [1] total_time:   total amount of time taken
        [3] flag:         "success", "timeout", or "deadend"
    """
    cur = start
    cur_time = 0
    cur_angle = None
    route = []

    while True:
        route.append(cur)

        if cur in end_nodes:  # Found a boba shop!
            return route, cur_time, "success"
        if cur_time >= timeout:  # Time exceeded
            return route, cur_time, "timeout"
        if len(adj[cur]) == 0:  # Dead end
            return route, cur_time, "deadend"

        # Out of all neighbors, small angle has higher weighting
        weights = np.ones(len(adj[cur]))
        for i, edge in enumerate(adj[cur]):
            _, _, angle = edge
            if 


if __name__ == "__main__":
    with open("./places.json") as fin:
        places = json.load(fin)

    for placename, slug in places:
        print(f"Reading boba locations...")
        with open(f"./data/boba/{slug}.csv") as fin:
            boba_gdf = gpd.read_file(
                f"./data/{slug}.csv",
                GEOM_POSSIBLE_NAMES="geometry", 
                KEEP_GEOM_COLUMNS="NO"
            )

        with open(f"./data/adj_lists/{slug}.json") as fin:
            adj = json.load(fin)
        