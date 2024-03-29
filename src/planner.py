from collections import Counter
from tinydb import Query
from metrodb import metrodb, cat_sort
from recipe import Recipe, recipe_string
    
# given a dict {sections -> (recipe, n_servings)}, compute:
#   - a menu overview markdown string
#   - the total weight of all ingredients
#   - the total number of servings
#   - the maximal number of servings per dish
#   - a markdown list of all special materials from all recipes
#   - a markdown shopping list, sectioned by ingredient category
#   - a markdown collection of recipes.
def compile_lists(menu: dict[str, tuple[Recipe, float]]):

    menu_list = ""     # list of recipes and servings for the menu overview page
    total_weight = 0   # total weight of all ingredients
    total_servings = 0 # total nuber of servings
    max_servings = 0   # maximal number of servings per dish
    materials = set()  # all special materials of all recipes
    allergens = []     # all allergens from all ingredients
    total_ingredients = Counter() # all ingredients and weights for the shopping list
    recipe_list = ""   # markdown formatted recipe list ("cookbook")
    
    for category in menu:
        if category != "misc":
        
            menu_list += "\n### " + str(category).capitalize() + "\n\n"
            recipe_list += "\n# " + str(category).capitalize() + "\n\n"

        cat_recipes = []
        for (recipe, n_servings) in menu[category]:

            # collect ingredients for shopping list
            for (_, ingredients) in recipe.scaled_ingredients(n_servings):
                total_ingredients += ingredients

            for allergen in recipe.allergens:
                allergens.append(allergen) if allergen not in allergens else allergens

            # collect materials
            materials |= recipe.materials

            if category != "misc":
                # update stats
                total_weight += n_servings * recipe.total_weight
                total_servings += n_servings
                max_servings = max(max_servings, n_servings)

                # collect recipe for menu overview
                menu_list += f"- {n_servings:g} Portionen {recipe.name.capitalize()}\n"

                # collect recipe string
                if n_servings != 0 and recipe.name != "misc":
                    cat_recipes.append(recipe_string(recipe, n_servings, True))

        # pagebreak after each category
        recipe_list += ("---").join(cat_recipes)

    # make a total materials list for the overview
    materials_list = "" if materials == set() else "\n## Spezialequipment\n\n" +\
                                                    "\n".join([f"- {item.capitalize()}" for item in materials])

    return menu_list, materials_list, total_weight, total_servings, max_servings, allergens, shopping_list(total_ingredients), recipe_list


def shopping_list(total_ingredients: Counter):
    cat_dict = dict()
    # insert into cat dict         
    def insert(cat, ingredient, amount):
        if cat in cat_dict:
            cat_dict[cat].append((ingredient, amount))
        else:
            cat_dict[cat] = [(ingredient, amount)]

    # split ingredients wrt market categories
    User = Query()
    for (ingredient, amount) in total_ingredients.items():
        db_entries = metrodb.search(User.ingredient == ingredient)
        if db_entries == []:
            insert("none", ingredient, amount)
        else:
            cat = db_entries[0]["category"]
            insert(cat, ingredient, amount)

    # print one category
    def cat_markdown(cat: str):
        md = ""
        cat_amount = 0
        for (ingredient, amount) in cat_dict[cat]:
            md += f"- [ ] {round(amount,3):g} kg {ingredient.capitalize()}\n"
            cat_amount += amount
        md = f"\n### {cat.capitalize()} ({round(cat_amount,3):g} kg)\n\n" + md
        return md

    # print all categories
    slist = ""
    for cat in sorted(cat_dict.keys(), key=cat_sort):
        if cat == "none": # put unknown category first
            slist = cat_markdown(cat) + slist
        else:
            slist += cat_markdown(cat)
           
    return slist


def plan(menu: dict[str, tuple[Recipe, float]]) -> str:
    
    (menu_list, materials_list, total_weight, total_servings,\
                    max_servings, allergens, shopping_list, recipe_list) = compile_lists(menu)
    
    text = "# Menü\n\n"
    text += menu_list

    text += f"\n\n {materials_list} \n\n"
    
    text += "### Stats\n\n"
    text += f"***Allergene:*** " + ", ".join([a.capitalize() for a in allergens]) + "\n\n"
    text += f"***Portionen insgesamt:*** {total_servings:g}\n\n"
    text += f"***Maximale Portionen pro Rezept:*** {max_servings:g}\n\n"
    text += f"***Gesamtgewicht der Zutaten:*** {total_weight:g} kg \n\n"
    text += f"***Geschätztes Gesamtvolumen der Zutaten:*** {(round(5*total_weight,0)):g} liter \n\n"
    text += md_pagebreak
    
    # printing two shopping lists cuz it handy
    #text += shopping_list
    #text += md_pagebreak
    text += "\n# Einkaufsliste\n\n"
    text += shopping_list
    text += md_pagebreak
    
    text += recipe_list
    
    return text

md_pagebreak = "\n<div style=\"page-break-after: always; visibility: hidden\">\n\pagebreak</div>\n"

general_text = """
## Ort klären:
- Wasseranschluss
- Abwasserentsorgung
- Gas
- Brenner-Unterlage
- Stromanschluss
- Müllentsorgung
- Tische/Bänke
- Lagerraum
- Zufahrt für das Auto/Lastenrad
- Unterstand/Zelt
- Licht



pürierstab
schneebesen
3 tuppen
faltzelt
Brenner: 2 hocker 1 paella
pfanne
3 ineinanderpassende edelstahltöpfe <= 80l mit deckel
2 thermoboxen
kaffe-stuff
eimer und schüsseln
6 Gns groß & 10 klein + alle deckel
sieb
4 vorlegekellen, 6 vorlegelöffel
paddel
bratkelle
schäler
messer
große kelle
6 schnippelbretter
300 teller & besteck
250~300 0,5 l Becher und 100~150 0,3l Becher
dosenöffner
reibe
kartoffelmatschi
kisten
"""


