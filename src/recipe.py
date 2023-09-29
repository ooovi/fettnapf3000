from collections import Counter

class Recipe:
    def __init__(self, name: str, n_servings: int, ingredients: [(str,Counter)], instructions: str, materials: set[str]):
        self.name = name.lower()
        self.n_servings = n_servings
        self.ingredients = [(section, Counter({i.lower() : c for (i,c) in ings.items()})) for (section, ings) in ingredients]
        self.instructions = instructions
        self.materials = materials
        self.total_weight = round(sum([sum(count for (ingredient,count) in ings.items()) for (cat,ings) in self.ingredients])/n_servings,3)

    def scaled_ingredients(self, n_servings: float) -> Counter:
        scaled = []
        for (section, ingredients) in self.ingredients:
            scaled.append((section, Counter({i : n_servings * (ingredients[i] / self.n_servings) for i in ingredients})))
        return scaled

    @classmethod
    def from_document(cls, doc):
        return cls(doc["name"], doc["n_servings"], doc["ingredients"], doc["instructions"], set(doc["materials"]))

# make a nice markdown recipe
def recipe_string(recipe: Recipe, n_servings=None, pretty=False) -> str:

    if not n_servings:
        n_servings = recipe.n_servings

    scaled_recipe = recipe.scaled_ingredients(n_servings)
    
    # name header
    recipe_str = f"\n## {recipe.name.capitalize()}\n{n_servings:g} Portionen\n"

    if pretty: # make a pretty table
        recipe_str += "\n"
        for (subsection, scaled_ingredients) in scaled_recipe:
            if subsection != "":
                recipe_str += "\n#### " + subsection.capitalize() + "\n"
            # ingredients table
            recipe_str += "| kg | Zutat | *kg pro Portion* |\n"
            recipe_str += "|:----|:-------------|:---------------:|\n"
            recipe_str += "\n".join(f"| {round(amount,3):g} | {ingredient.capitalize()} |  *{round(amount/n_servings,3):g}* |"\
                                      for (ingredient, amount) in scaled_ingredients.items())
            recipe_str += "\n"
            
        recipe_str += f"\nGesamtgewicht: {n_servings * recipe.total_weight:g} kg\n"
        recipe_str += f"\nGewicht pro Portion: {recipe.total_weight:g} kg\n"

    else: # just make a human readable string
        recipe_str += "\n### Zutaten\n"
        for (subsection, scaled_ingredients) in scaled_recipe:
            if subsection != "":
                recipe_str += "\n#### " + subsection.capitalize() + "\n"
            recipe_str += "\n".join(f"{amount} {ingredient}" for (ingredient, amount) in scaled_ingredients.items())
            recipe_str += "\n"

    recipe_str += "\n"
    
    # instructions
    if recipe.instructions != "":
        recipe_str += "### Anleitung\n"
        recipe_str += f"{recipe.instructions}\n\n"
        
    # materials
    if recipe.materials != set():
        recipe_str += "### Material\n"
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
    }
