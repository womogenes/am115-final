import random
import os
import numpy as np

import json
import pickle
import geopandas as gpd
import osmnx as ox

from tqdm import tqdm

from data import get_data
from utils import angle_diff

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


# Keep visiting nodes till we hit something in end_nodes
def random_walk(adj, end_nodes, start, timeout=60*2.5, angle_cutoff=np.pi/3, forward_weight=5):
    """
    Do a random walk starting from node <start> (node id)
        until we hit a boba shop, hit a dead end, or time out.
    
    angle_cutoff and forward_weight are used to determine how
        much more likely the agent is to walk forward than to
        take a turn.

    Timeout is in seconds. If we haven't reached a boba shop or
        a dead end by that time, we terminate.
    
    Returns an ordered tuple:
        [0] route:        list of tuples (node id, time)
        [1] total_time:   total amount of time taken
        [2] flag:         "success", "timeout", or "deadend"
    """
    cur = start
    prev = None  # Don't want to go backwards
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
            nbr, _, angle1, _ = edge
            if cur_angle != None and abs(angle_diff(cur_angle, angle1)) < angle_cutoff:
                weights[i] = forward_weight
            if nbr == prev:
                weights[i] = 1e-9

        chosen_edge_idx = np.random.choice(range(len(adj[cur])), p=(weights / weights.sum()))
        nbr, length, _, angle2 = adj[cur][chosen_edge_idx]
        cur_time += length / 4 / 1000 * 60  # Walking speed is 4 kph, convert to minutes

        cur_angle = angle2
        prev = cur
        cur = nbr


def random_walks(place, n_starts, n_samples, timeout=60*2.5):
    # Do many random walks from many starting locations
    placename, coords, slug = place
    print(f"Doing walks from {placename}...")

    G, adj, boba_gdf = get_data(slug)
    end_nodes = get_end_nodes(G, boba_gdf)
    print(f"Data imported.")

    # Sample lots of starting locations
    starts = random.choices(list(G.nodes()), k=n_starts)
    records = {}
    for start in tqdm(starts, ncols=100):
        times = []
        steps = []
        flags = []
        for _ in range(n_samples):
            route, total_time, flag = random_walk(adj, end_nodes, start, timeout=timeout)
            times.append(total_time)
            steps.append(len(route))
            flags.append(flag)
        
        records[start] = {
            "times": times,
            "steps": steps,
            "flags": flags
        }
    
    print(f"Saving {n_starts * n_samples:,} walks...")
    os.makedirs(f"./output/walk_trials", exist_ok=True)
    with open(f"./output/walk_trials/{slug}.pkl", "w") as fout:
        pickle.dump(records, fout, separators=(",", ":"))

    return records
