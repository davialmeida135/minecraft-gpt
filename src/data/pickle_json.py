import json
import pickle
from pathlib import Path


def load_and_pickle_recipes(json_path: str, pickle_path: str) -> dict:
    """
    Load recipes.json and save as pickled dictionary.

    Args:
        json_path: Path to recipes.json
        pickle_path: Path to output pickle file

    Returns:
        Dictionary loaded from JSON
    """
    json_file = Path(json_path)
    pickle_file = Path(pickle_path)

    # Load JSON
    with open(json_file, "r") as f:
        recipes_dict = json.load(f)

    # Pickle the dictionary
    with open(pickle_file, "wb") as f:
        pickle.dump(recipes_dict, f)

    return recipes_dict


if __name__ == "__main__":
    recipes = load_and_pickle_recipes(
        "data/raw/recipes.json", "data/processed/recipes.pkl"
    )
    print(f"Loaded {len(recipes)} recipes")
