import pickle
import geopandas as gpd

def get_data(slug):
    """
    Return G, adj, boba_gdf.
    """    
    # print(f"Reading boba locations...")
    boba_gdf = gpd.read_file(
        f"./data/boba/{slug}.csv",
        GEOM_POSSIBLE_NAMES="geometry",
        KEEP_GEOM_COLUMNS="NO"
    )

    # print(f"Reading network...")
    with open(f"./data/networks/{slug}.pkl", "rb") as fin:
        G = pickle.load(fin)

    # print(f"Reading adjacency list...")
    with open(f"./data/adj_lists/{slug}.pkl", "rb") as fin:
        adj = pickle.load(fin)

    return G, adj, boba_gdf
