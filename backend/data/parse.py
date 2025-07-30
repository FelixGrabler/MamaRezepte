import json


def format_ingredient(ingredient):
    if "," in ingredient:
        return f"__{ingredient}"
    else:
        parts = ingredient.split()
        if len(parts) == 1:
            return f"__{parts[0]}"
        elif len(parts) == 2:
            return f"{parts[0]}__{parts[1]}"
        else:
            return parts[0] + "_" + parts[1] + "_" + " ".join(parts[2:])


def parse_recipe(recipe_text, parent_title=None):
    parts = recipe_text.strip().split("\n\n")
    title = parts[0].lstrip("+").strip()
    ingredients = [format_ingredient(ing) for ing in parts[1].split("\n") if ing]
    instructions = parts[2] if len(parts) > 2 else ""
    return {
        "title": title,
        "ingredients": ingredients,
        "instructions": instructions,
        "parent_recipe": parent_title,
    }


def parse_recipes(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        recipes_text = file.read().strip().split("\n\n\n")

    structured_recipes = []
    parent_title = None
    for recipe_text in recipes_text:
        if recipe_text.startswith("+"):
            structured_recipes.append(parse_recipe(recipe_text, parent_title))
        else:
            parsed_recipe = parse_recipe(recipe_text)
            parent_title = parsed_recipe["title"]
            structured_recipes.append(parsed_recipe)

    return structured_recipes


def save_json(file_path, data):
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(data)


# Replace 'rezepte.txt' with the path to your file
recipes = parse_recipes("rezepte.txt")
json_output = json.dumps(recipes, indent=4, ensure_ascii=False)
save_json("recipes.json", json_output)
