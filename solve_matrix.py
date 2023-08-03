import os
import json
import numpy as np
from scipy import sparse
import pickle
from collections import defaultdict

import osmnx as ox

from tqdm import tqdm
import matplotlib.pyplot as plt

from data import get_data
from random_walks import get_end_nodes, angle_diff


def create_states(adj):
    """
    Create list of states [(u1, v1), (u1, v2), ..., (un, vn)].
    """
    incoming = defaultdict(list)
    for node in adj:
        for edge in adj[node]:
            incoming[edge[0]].append(node)
    for node in incoming:
        incoming[node].sort()
    
    states = []
    for node in sorted(adj.keys()):
        states.extend([(node, prev) for prev in incoming[node]])

    return states


def matrix_method(adj, states, end_nodes, angle_cutoff, forward_favor):
    state2idx = {state: idx for idx, state in enumerate(states)}
    
    N = len(states)
    A = sparse.lil_array((N + 1, N + 1))

    for i, state in enumerate(states):
        assert(i == state2idx[state])
        node, prev = state

        if node in end_nodes:
            continue

        # Weigh next routes
        cur_angle = next(angle2 for nbr, _, _, angle2 in adj[prev] if nbr == node)

        weights = []
        travel_times = []
        for nbr, length, angle1, angle2 in adj[node]:
            if nbr == prev:
                weight = 1e-9
            elif abs(angle_diff(cur_angle, angle1)) < angle_cutoff:
                weight = forward_favor
            else:
                weight = 1
            weights.append(weight)
            travel_times.append(length / 4 / 1000 * 60)
        
        # Normalize weights, calculate expected travel time
        weights = np.array(weights) / np.sum(weights)
        E_travel_time = weights @ np.array(travel_times)

        # Record probability of going to (nbr, node) from (node, prev)
        for j, edge in enumerate(adj[node]):
            nbr = edge[0]
            A[state2idx[(node, prev)],state2idx[(nbr, node)]] = weights[j]
        
        # Record expected travel time
        A[state2idx[(node, prev)],-1] = E_travel_time
        
        assert np.isclose(weights.sum(), 1)

    ## MEAT OF THE MATH
    b = sparse.lil_array((N + 1, 1))
    b[-1] = -1

    v = sparse.linalg.spsolve(A - sparse.eye(N + 1), b)
    ## EXPLAINED IN REPORT

    return v[:-1]


def deg_to_rad(theta):
    return theta * np.pi / 180


if __name__ == "__main__":
    os.makedirs("./output/matrix_method", exist_ok=True)

    with open("./places.json") as fin:
        places = json.load(fin)
    
    for i, place in enumerate(places):
        placename, coords, slug = place
        print(f"[{i:>2}/{len(places)}] Executing matrix method on {placename} (slug: {slug})")
        save_path = f"./output/matrix_method/{slug}.pkl"

        if os.path.exists(save_path):
            print(f"  Already exists, skipping.")
            continue

        G, adj, boba_gdf = get_data(slug)
        end_nodes = get_end_nodes(G, boba_gdf)
        states = create_states(adj)

        results = {"expected_time": {}, "states": states}
        for angle_deg in [0, 30, 60, 90]:
            for forward_favor in [1e-4, 0.5, 1, 2, 3, 4, 5, 8, 20]:
                print(f"  * angle_deg={angle_deg}, forward_favor={forward_favor}".ljust(60), end="")

                expected_time = matrix_method(
                    adj, states, end_nodes,
                    angle_cutoff=deg_to_rad(angle_deg),
                    forward_favor=forward_favor
                )
                results["expected_time"][(angle_deg, forward_favor)] = expected_time
            
                print(f"avg. time: {np.mean(expected_time):3f} mins")
        
        os.makedirs("./output/matrix_method", exist_ok=True)
        print(f"Done. Saving to {save_path}...")
        with open(save_path, "wb") as fout:
            pickle.dump(results, fout)
        
        print()
