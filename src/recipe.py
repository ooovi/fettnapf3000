from collections import Counter
from tinydb import Query
from metrodb import get_ingredient

from i18n import get_i18n

class Recipe:
    def __init__(self, name: str, n_servings: int, ingredients: [(str,Counter)], instructions: str, materials: set[str], category="misc"):
        self.name = name.lower()
        self.n_servings = n_servings
        self.ingredients = []
        self.instructions = instructions
        self.materials = set(material.lower() for material in materials)
        self.category = category.lower()
        self.total_weight = round(sum([sum(count for (ingredient,count) in ings.items()) for (cat,ings) in ingredients])/n_servings,3)

        allergens = []
        User = Query()

        for (section, ings) in ingredients:
            counter = Counter()
            for (ing, s) in ings.items():
                name = ing

                db_ingredient = get_ingredient(ing)
                if db_ingredient:
                    # if in database use the (possibly translated) name
                    name = db_ingredient["names"]['de']

                    ing_allergens = db_ingredient["allergens"]
                    for allergen in ing_allergens:
                        if not (allergen in allergens):
                            allergens.append(allergen) if allergen not in allergens else allergens
                counter[name] += s

            self.ingredients.append((section, counter))
        allergens.sort()
        self.allergens = allergens

    def scaled_ingredients(self, n_servings: float) -> Counter:
        scaled = []
        for (section, ingredients) in self.ingredients:
            scaled.append((section, Counter({i : n_servings * (ingredients[i] / self.n_servings) for i in ingredients})))
        return scaled

    @classmethod
    def from_document(cls, doc):
        if "category" in doc:
            cat = doc["category"]
        else:
            cat = "misc"
        return cls(doc["name"], doc["n_servings"], doc["ingredients"], doc["instructions"], set(doc["materials"]), cat)

# make a nice markdown recipe
def recipe_string(recipe: Recipe, lang, n_servings=None, pretty=False) -> str:
    _ = get_i18n(lang).gettext
    ngettext = get_i18n(lang).ngettext
    if not n_servings:
        n_servings = recipe.n_servings

    scaled_recipe = recipe.scaled_ingredients(n_servings)
    
    # name header
    recipe_str = f"\n## {recipe.name.capitalize()}\n{ngettext("%(num)d serving", "%(num)d servings", n_servings) % {'num': n_servings}}\n"

    if pretty: # print allergens
        recipe_str += f"\n{_("Allergens")}: " + ", ".join([allergen.capitalize() for allergen in recipe.allergens]) + "\n"
    
    if pretty: # make a pretty table
        recipe_str += "\n"
        for (subsection, scaled_ingredients) in scaled_recipe:
            if subsection != "":
                recipe_str += "\n#### " + subsection.capitalize() + "\n"
            # ingredients table
            recipe_str += f"| kg | {_("Ingredient")} | *{_("kg per serving")}* |\n"
            recipe_str += "|:----|:-------------|:---------------:|\n"
            for (ingredient, amount) in scaled_ingredients.items():
                db_ingredient = get_ingredient(ingredient)
                if db_ingredient:
                    name = db_ingredient["names"][lang] or db_ingredient["names"]['de']
                else:
                    name = ingredient
                recipe_str += f"| {round(amount,3):g} | {name.capitalize()} |  *{round(amount/n_servings,3):g}* |"  
                recipe_str += "\n"
            
        recipe_str += f"\n{_("Total weight")}: {n_servings * recipe.total_weight:g} kg\n"
        recipe_str += f"\n{_("Weight per serving")}: {recipe.total_weight:g} kg\n"

    else: # just make a human readable string
        recipe_str += f"{_("Category")}: " + recipe.category.capitalize() + "\n"
        recipe_str += f"\n### {_("Ingredients")}\n"
        for (subsection, scaled_ingredients) in scaled_recipe:
            if subsection != "":
                recipe_str += "\n#### " + subsection.capitalize() + "\n"
            for (ingredient, amount) in scaled_ingredients.items():
                db_ingredient = get_ingredient(ingredient)
                if db_ingredient:
                    name = db_ingredient["names"][lang] or db_ingredient["names"]['de']
                else:
                    name = ingredient
                recipe_str += f"{amount} {name}"
                recipe_str += "\n"

    recipe_str += "\n"
    
    # instructions
    if recipe.instructions != "":
        recipe_str += f"### {_("Instructions")}\n"
        recipe_str += f"{recipe.instructions}\n\n"
        
    # materials
    if recipe.materials != set():
        recipe_str += f"### {_("Materials")}\n"
        recipe_str += "\n".join(f"{name.capitalize()}" for name in recipe.materials) + "\n\n"
        
    recipe_str += "\n\n"
    
    return recipe_str

def recipe_dict(recipe: Recipe) -> dict:
    return {
        "name" : recipe.name,
        "n_servings" : recipe.n_servings,
        "ingredients" : recipe.ingredients,
        "instructions" : recipe.instructions,
        "materials" : [m for m in recipe.materials],
        "category" : recipe.category
    }
