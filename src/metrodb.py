from tinydb import Query, TinyDB

metrodb = TinyDB('../../fettnapf3000recipes/metrodb.json', indent=2)

def ingredients_list():
    ingredients = [ing["ingredient"] for ing in metrodb.search(Query().ingredient.exists())]
    ingredients.sort()
    return ingredients

def allergens_list():
    allergens = [a for a in set().union(*[set(entry["allergens"]) for entry in metrodb.search(Query().allergens.exists())])]
    allergens.sort()
    return allergens

def categories_list():
    categories = [c for c in set([entry["category"] for entry in metrodb.search(Query().category.exists())])]
    categories.sort()
    return categories
