"""
scripts.loading.py

Loading module of the database for the INSPIRE LA dataset.

Note: some functions will be taken from the Jupyter notebooks of the `exploration` branch of the project.
Date: 15/08/2024
"""

import json
import requests
import pandas as pd


def load_data(
    local=False,
    local_path="data/inspire_LA.json",
    remote_url="https://github.com/restrepo/inspireauth/raw/main/data/inspire_LA.json",
):
    """
    Load the dataset from a local file or a remote URL.

    Parameters:
    local (bool): If True, loads the data from the local file path. If False, loads from the remote URL.
    local_path (str): Path to the local JSON file.
    remote_url (str): URL to the remote JSON file.

    Returns:
    pd.DataFrame: The loaded dataset as a pandas DataFrame.
    """
    print("Loading data...")
    if local:
        with open(local_path, "r") as f:
            data = json.load(f)
    else:
        r = requests.get(remote_url)
        data = r.json()

    df = pd.DataFrame(data)
    print("Data loaded successfully!")
    return df


# Example usage (this would be in your main script, not in the module):
# db_master = load_data(local=False)


def load_world_papers():
    """
    Load the DataFrame of all the papers in the world.

    Returns:
        pd.DataFrame: The DataFrame of all the papers of the world. The index is the year and the column is the number of papers.
    """
    df_world = pd.read_csv("world_papers.csv")
    df_world = df_world[["year", "Citable papers"]]
    df_world = df_world.rename(columns={"Citable papers": "World"})
    df_world = df_world.set_index("year")
    df_world = df_world[df_world.index <= 2021]

    return df_world
