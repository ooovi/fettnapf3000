from collections import Counter
from tinydb import Query
from metrodb import metrodb, cat_sort

class Recipe:
    def __init__(self, name: str, ingredients: Counter, instructions: str, materials: set[str]):
        self.name = name
        self.ingredients = ingredients
        self.instructions = instructions
        self.materials = materials
        self.total_weight = sum([count for (ingredient,count) in ingredients.items()])

    def scaled_ingredients(self, n_servings: float):
        return Counter({i : n_servings * self.ingredients[i] for i in self.ingredients})

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
    total_ingredients = Counter() # all ingredients and weights for the shopping list
    recipe_list = ""   # markdown formatted recipe list ("cookbook")
    
    for category in menu:
        if category != "misc":
        
            menu_list += "\n### " + str(category).capitalize() + "\n\n"
            recipe_list += "\n# " + str(category).capitalize() + "\n\n"

        for (recipe, n_servings) in menu[category]:

            # collect ingredients for shopping list
            total_ingredients += recipe.scaled_ingredients(n_servings)

            # collect materials
            materials |= recipe.materials

            if category != "misc":
                # update stats
                total_weight += n_servings * recipe.total_weight
                total_servings += n_servings
                max_servings = max(max_servings, n_servings)

                # collect recipe for menu overview
                menu_list += f"- {n_servings:g} servings -- {recipe.name.capitalize()}\n"

                # collect recipe string
                if n_servings != 0 and recipe.name != "misc":
                    scaled_ingredients = recipe.scaled_ingredients(n_servings).items()

                    # name header
                    recipe_list += f"\n## {recipe.name.capitalize()}\n\n {n_servings:g} servings\n\n"

                    # ingredients table
                    recipe_list += "| kg | Ingredients | *per serving* |\n"
                    recipe_list += "|----|-------------|---------------|\n"
                    recipe_list += "\n".join([f"| {amount:g} | {ingredient.capitalize()} | *{recipe.ingredients[ingredient]:g}* |"\
                                              for (ingredient, amount) in scaled_ingredients])
                    recipe_list += "\n| -------- | | -------- |\n"
                    recipe_list += f"| {n_servings * recipe.total_weight:g} | | {recipe.total_weight:g} |\n"
                    recipe_list += "\n\n"

                    # instructions
                    if recipe.instructions != "":
                        recipe_list += "### Instructions\n\n"
                        recipe_list += f"{recipe.instructions.capitalize()} \n\n"

                    # materials
                    if recipe.materials != set():
                        recipe_list += "### Special materials\n\n"
                        recipe_list += "\n".join(f"{name.capitalize()}" for name in recipe.materials) + "\n\n"

                    recipe_list += "\n\n"

        # pagebreak after each category
        recipe_list += md_pagebreak

    # make a total materials list for the overview
    materials_list = "" if materials == set() else "\n## Special materials\n\n" +\
                                                    "\n".join([f"- {item.capitalize()}" for item in materials])

    return menu_list, materials_list, total_weight, total_servings, max_servings, shopping_list(total_ingredients), recipe_list


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
        md = f"\n### {cat.capitalize()}\n\n"
        for (ingredient, amount) in cat_dict[cat]:
            md += f"- {amount:g} {ingredient.capitalize()}\n"
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
                    max_servings, shopping_list, recipe_list) = compile_lists(menu)
    
    text = markdown_header
    text += "# Menu\n\n"
    text += menu_list

    text += f"\n\n {materials_list} \n\n"
    
    text += "## Stats\n\n"
    text += f"***Total number of servings:*** {total_servings:g}\n\n"
    text += f"***Maximal number of servings per recipe:*** {max_servings:g}\n\n"
    text += f"***Total ingredient weight:*** {total_weight:g} kg \n\n"
    text += md_pagebreak
    
    # printing two shopping lists cuz it handy
    text += shopping_list
    text += md_pagebreak
    text += shopping_list
    text += md_pagebreak
    
    text += recipe_list
    
    return text


markdown_header = """
---
fontsize: 12pt
header-includes: |
   \\usepackage[margin=0.7in]{geometry}
---
"""

md_pagebreak = "\n<div style=\"page-break-after: always; visibility: hidden\">\n\pagebreak</div>\n"

general_text = """
## Ort kl??ren:
- Wasseranschluss
- Abwasserentsorgung
- Gas
- Brenner-Unterlage
- Stromanschluss
- M??llentsorgung
- Tische/ B??nke
- Lagerraum
- Zufahrt f??r das Auto/Lastenrad
- Unterstand/Zelt
- Licht



p??rierstab
schneebesen
3 tuppen
faltzelt
Brenner: 2 hocker 1 paella
pfanne
3 ineinanderpassende edelstahlt??pfe <= 80l mit deckel
2 thermoboxen
kaffe-stuff
eimer und sch??sseln
6 Gns gro?? & 10 klein + alle deckel
sieb
4 vorlegekellen, 6 vorlegel??ffel
paddel
bratkelle
sch??ler
messer
gro??e kelle
6 schnippelbretter
300 teller & besteck
250~300 0,5 l Becher und 100~150 0,3l Becher
dosen??ffner
reibe
kartoffelmatschi
kisten
"""


