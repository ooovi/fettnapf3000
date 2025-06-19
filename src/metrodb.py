from tinydb import TinyDB, Query

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


def get_ingredient(name):
    """
    search for ingredient in any language
    """
    q = Query()
    db_entries = metrodb.search(( q.ingredient == name) | (q.english == name))
    if db_entries:
        entry = db_entries[0]
        
        names = {
            'de': entry['ingredient'],
        }
        if entry['english']:
            names['en'] = entry['english']

        return {
            'id': entry.doc_id,
            'names': names,
            'category': entry['category'],
            'allergens': entry['allergens']
        }
    else:
        return None