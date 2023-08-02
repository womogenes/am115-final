import osmnx as ox
import datetime as dt
import time
import os
import json
import pickle as pkl

def download(placename, slug, verbose=False, overwrite=False):
    save_path = f"./data/networks/{slug}.pkl"
    if not overwrite and os.path.exists(save_path):
        if verbose: print(f"  File already exists. Skipping...")
        return
    
    G = ox.graph.graph_from_address(
        address=placename,
        dist=10000,
        dist_type="network",
        # network_type="drive",
        custom_filter='["highway"~"footway"]'
    )
    # Remove duplicate edges
    og_edges = list(G.edges)
    for u, v, i in og_edges:
        if i > 0:
            G.remove_edge(u, v, i)            
    if verbose: print(f"  Finished downloading in {time.time() - start_time:.3f} seconds")

    if verbose: print(f"  Saving to {save_path}...")
    with open(save_path, "wb") as fout:
        pkl.dump(G, fout)
    if verbose: print()


if __name__ == "__main__":
    with open("./places.json") as fin:
        places = json.load(fin)
    
    for placename, slug in places:
        start_time = time.time()
        print(f"[{dt.datetime.now():%H:%M:%S}] Downloading \"{placename}\", slug: {slug}")

        try:
            download(placename, slug, verbose=True)

        except Exception as err:
            print(f"\n===== ERRROR [{dt.datetime.now():%H:%M:%S}] =====")
            print(err)
            print(f"=============================\n")
