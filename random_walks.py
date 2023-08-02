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


if __name__ == "__main__":
    print(f"Reading boba locations...")
    with open(f"./data/boba/{slug}.csv") as fin:
        boba_gdf = gpd.read_file(
            f"./data/{slug}.csv",
            GEOM_POSSIBLE_NAMES="geometry", 
            KEEP_GEOM_COLUMNS="NO"
        )
