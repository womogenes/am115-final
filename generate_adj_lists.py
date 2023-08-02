import pickle as pkl
import json
from collections import defaultdict
import geopandas as gpd
import osmnx as ox

from tqdm import tqdm


def get_end_nodes(G, boba_gdf):
    end_nodes = set()
    for _, row in boba_gdf.iterrows():
        x, y = row["geometry"].x, row["geometry"].y
        node, dist = ox.nearest_nodes(G, x, y, return_dist=True)

        end_nodes.add(node)
        for edge in G.in_edges(node):
            end_nodes.add(edge[0])

    return end_nodes


def generate_adjacency_list(G, boba_gdf):
    
    # Find nearest nodes to boba shops
    end_nodes = get_end_nodes(G, boba_gdf)

    seen_edges = set()
    adj = defaultdict(list)
    for u, v in tqdm(G.edges()):
        if (u, v) in seen_edges: continue
        seen_edges.add((u, v))
        edge_data = edges.loc[u].loc[v]




if __name__ == "__main__":
    with open("./places.json") as fin:
        places = json.read(fin)

        for placename, slug in places:
            print(f"Creating adjacency list for {placename} (slug: {slug})")
            
            print(f"Reading graph file...")
            with open(f"./data/networks/{slug}.pkl", "rb") as fin:
                G = pkl.load(fin)
                G = ox.project_graph(G)
            nodes, edges = ox.graph_to_gdfs(G)

            print(f"Reading boba locations...")
            with open(f"./data/boba/{slug}.csv") as fin:
                boba_gdf = gpd.read_file(
                    f"./data/{slug}.csv",
                    GEOM_POSSIBLE_NAMES="geometry", 
                    KEEP_GEOM_COLUMNS="NO"
                )
