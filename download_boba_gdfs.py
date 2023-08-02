"""
For each place, download boba within a certain distance of that place.
"""

import os
import json
import numpy as np
import pickle
import pandas as pd
import requests
from tqdm import tqdm

import osmnx as ox
from shapely.geometry import Point

from dotenv import load_dotenv
load_dotenv()

API_KEY = os.environ["YELP_API_KEY"]

def download_boba_gdf(placename, slug):
    y, x = ox.geocoder.geocode(placename)
    shops = []
    for page in range(20):
        headers = {"Authorization": f"Bearer {API_KEY}"}
        search_api_url = "https://api.yelp.com/v3/businesses/search"
        params = {
            "term": "bubble tea",
            "categories": "bubbletea, boba",
            "latitude": y, "longitude": x,
            "radius": 10000,
            "offset": page * 50,
            "limit": 50
        }
        res = requests.get(search_api_url,
                                headers=headers,
                                params=params,
                                timeout=10)
        data = res.json()
        shops.extend(data["businesses"])

        # Stop iterating
        if (page + 1) * 50 > data["total"]:
            break
    
    gdf = pd.DataFrame.from_records(shops)
    gdf.sort_index()

    # Find more accurate locations
    print(f"Geocoding {len(gdf)} locations...")
    for index, row in tqdm(list(gdf.iterrows()), ncols=50):
        loc = row["location"]
        addr = f"{loc['address1']}, {loc['city']}, {loc['zip_code']}"
        try:
            lat, long = ox.geocoder.geocode(addr)
        except:
            long, lat = row["coordinates"]["longitude"], row["coordinates"]["latitude"]
        
        gdf.loc[index,"geometry"] = Point(long, lat)

    gdf = gdf[["id", "geometry", "alias", "name", "rating", "price"]]

    print(f"Dropping shops outside the network...")
    with open(f"./data/networks/{slug}.pkl", "rb") as fin:
        G = pickle.load(fin)
    X, Y = [g.x for g in gdf.geometry], [g.y for g in gdf.geometry]
    _, node_dists = ox.nearest_nodes(G, X, Y, return_dist=True)
    node_dists = np.array(node_dists)
    gdf.drop(index=np.where(node_dists >= 200)[0], inplace=True)

    os.makedirs(f"./data/boba", exist_ok=True)
    save_path = f"./data/boba/{slug}.csv"
    gdf.to_csv(save_path, index=False)
    print(f"Saved {len(gdf)} boba shops in {placename} to {save_path}")


if __name__ == "__main__":
    with open("./places.json") as fin:
        places = json.load(fin)

    for i, place in enumerate(places):
        placename, slug = place
        
        print(f"[{i:>2}/{len(places)}] Getting boba locations near {placename} (slug: {slug})")
        download_boba_gdf(placename, slug)
        print()
