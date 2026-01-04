import json
from pathlib import Path


def load_items_mapping(items_path: str) -> dict[int, str]:
    """
    Load items.json and create a mapping from item ID to item name.

    Args:
        items_path: Path to items.json

    Returns:
        Dictionary mapping item ID (int) to item name (str)
    """
    with open(items_path, "r", encoding="utf-8") as f:
        items = json.load(f)

    return {item["id"]: item["name"] for item in items}


def replace_ids_in_shape(shape: list, id_to_name: dict[int, str]) -> list:
    """
    Recursively replace item IDs with names in a crafting shape.

    Args:
        shape: The inShape or outShape list (can be nested)
        id_to_name: Mapping from item ID to name

    Returns:
        Shape with IDs replaced by names
    """
    result = []
    for item in shape:
        if item is None:
            result.append(None)
        elif isinstance(item, list):
            result.append(replace_ids_in_shape(item, id_to_name))
        elif isinstance(item, int):
            result.append(id_to_name.get(item, f"unknown_{item}"))
        else:
            result.append(item)
    return result


def transform_recipes(items_path: str, recipes_path: str, output_path: str) -> dict:
    """
    Transform recipes.json by replacing all item IDs with item names.

    Args:
        items_path: Path to items.json
        recipes_path: Path to recipes.json
        output_path: Path for output JSON file

    Returns:
        Transformed recipes dictionary
    """
    # Load item ID to name mapping
    id_to_name = load_items_mapping(items_path)
    print(f"Loaded {len(id_to_name)} items")

    # Load recipes
    with open(recipes_path, "r", encoding="utf-8") as f:
        recipes = json.load(f)
    print(f"Loaded {len(recipes)} recipe entries")

    # Transform recipes
    transformed = {}
    for result_id, recipe_list in recipes.items():
        # Convert the result ID key to item name
        result_id_int = int(result_id)
        result_name = id_to_name.get(result_id_int, f"unknown_{result_id}")

        transformed_recipes = []
        for recipe in recipe_list:
            transformed_recipe = {}

            # Transform inShape if present
            if "inShape" in recipe:
                transformed_recipe["inShape"] = replace_ids_in_shape(
                    recipe["inShape"], id_to_name
                )

            # Transform outShape if present
            if "outShape" in recipe:
                transformed_recipe["outShape"] = replace_ids_in_shape(
                    recipe["outShape"], id_to_name
                )

            # Transform ingredients if present (for shapeless recipes)
            if "ingredients" in recipe:
                transformed_recipe["ingredients"] = replace_ids_in_shape(
                    recipe["ingredients"], id_to_name
                )

            # Transform result
            if "result" in recipe:
                result = recipe["result"]
                transformed_recipe["result"] = {
                    "name": id_to_name.get(result["id"], f"unknown_{result['id']}"),
                    "count": result.get("count", 1),
                }

            transformed_recipes.append(transformed_recipe)

        transformed[result_name] = transformed_recipes

    # Save transformed recipes
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(transformed, f, indent=2)

    print(f"Saved transformed recipes to {output_path}")
    return transformed


if __name__ == "__main__":
    transformed = transform_recipes(
        "data/raw/items.json",
        "data/raw/recipes.json",
        "data/processed/recipes_named.json",
    )

    # Print a sample recipe
    print("\n=== Sample Recipes ===")
    for name, recipes in list(transformed.items())[:3]:
        print(f"\n{name}:")
        for recipe in recipes:
            print(f"  {recipe}")
