"""
For each place, download boba within a certain distance of that place.
"""

import os
import json
import pandas as pd
import osmnx as ox
import requests

from dotenv import load_dotenv
load_dotenv()

API_KEY = os.environ["YELP_API_KEY"]

def get_boba_gdf(placename, slug):
    y, x = ox.geocoder.geocode(placename)

    gdf = []

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

        # return a dictionary
        data_dict = res.json()
