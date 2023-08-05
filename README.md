# Random boba walks

## Setup

Python scripts require the `osmnx` package. Easiest way is to install with conda:
```bash
conda create -n ox -c conda-forge --strict-channel-priority osmnx
```

The Yelp Fusion API is used to find boba shops. To get an API key, go to https://docs.developer.yelp.com/docs/fusion-intro. Put the API key into `.env` (root project directory) with the content:
```.env
YELP_API_KEY=8UOQ...
```

## Running

Activate the conda environment, or ensure that the `osmnx` library is available.

1. `python download_street_networks.py`
2. `python download_boba_gdfs.py`
3. `python generate_adj_list.py`
4. `python solve_matrix.py`
5. `python shortest_paths.py`
6. Run through the notebook `test/make_plots.ipynb` and `analyze_matrix_results.ipynb` to create plots.
