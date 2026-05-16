import cherrypy
import string
from tinydb import Query
import urllib.parse
from collections import Counter

from pages.fettnapf import FettnapfPage
from utils import randomoji, randomoji_link, options, datalist
from recipe import Recipe, recipe_string, recipe_dict
from metrodb import metrodb, ingredients_list, allergens_list, categories_list, prep_list, prep_daybefore_list
import parser

allowed = set(string.ascii_lowercase + string.ascii_uppercase + string.digits + ".,äöüÄÖÜß !?€-/\"\'\n\r")

class RepertoirePage(FettnapfPage):
    
    def selection_page(self, dropdown_text: str, button_text: str, action: str, available_options: list):
        return self.html_body("repertoire",
            f"""{randomoji_link(".")}
                <form action="{action}" method="post">
                 <select name="name" id="select" required style="width:100%">
                  <option disabled selected value> -- {dropdown_text} -- </option>
                  {options(available_options)}
                 </select>
                 <p><input type="submit" value="{button_text}"></p>
                 </form>
                <form action="{self.root}/repertoire">
                 <p><input type="submit" value="Doch nicht."></p>
                </form>
            """)

    # a page for repertoire management
    @cherrypy.expose
    def index(self, **kwargs):
        text = ""
        if kwargs:
            text = kwargs["text"]
        return self.html_body("repertoire",
            f"""{randomoji_link(".")}
                <p style="text-align:center;">
                 <strong>{text}</strong>
                </p>
                <form action="add_recipe">
                 <p><input type="submit" value="Neues Rezept"></p>
                </form>
                <form action="delete_recipe" method="post">
                 <p><input type="submit" value="Rezept löschen"></p>
                </form>
                <form action="edit_recipe" method="post">
                 <p><input type="submit" value="Rezept editieren"></p>
                </form>
                     <hr>
                <form action="add_ingredient">
                 <p><input type="submit" value="Neue Zutat"></p>
                </form>
                <form action="delete_ingredient" method="post">
                 <p><input type="submit" value="Zutat löschen"></p>
                </form>
                <form action="edit_ingredient">
                 <p><input type="submit" value="Zutat editieren"></p>
                </form>
                     <hr>
                <form action="..">
                 <p><input type="submit" value="Kalkulation"></p>
                </form>
                 <br>
                <h1>Rezepte</h1>
                {self.recipe_list(True)}
            """)
    
    @cherrypy.expose
    def delete_ingredient(self):
        return self.selection_page("Zutat zum löschen auswählen",
                                   "Wirklich löschen!",
                                   "delete_ingredient_action",
                                   ingredients_list())

    @cherrypy.expose
    def delete_ingredient_action(self, **kwargs):
        ingredient_name = kwargs["name"]
        metrodb.remove(Query().ingredient == ingredient_name)
        raise cherrypy.HTTPRedirect(f"{self.root}/repertoire?text=" +
                                      urllib.parse.quote(f"Zutat {ingredient_name.capitalize()} gelöscht!"))

    # form for ingredient database, optionally pre-filled
    def ingredient_form(self, action, name = "", name_en = "", selected_category = "", selected_allergens = [], selected_prep = "", selected_prep_daybefore = ""):

        categories = datalist("categories", categories_list(), [selected_category])
        allergens = datalist("allergens", allergens_list(), selected_allergens)
        prep = datalist("prep", prep_list(), [selected_prep])
        prep_daybefore = datalist("prep_daybefore", prep_daybefore_list(), [selected_prep_daybefore])
        edit_name = """<input type="hidden" id="edit" value="aaa" name="edit">""" if name else ""
        
        return self.html_body("repertoire",
            f"""<p style="font-size:5em; text-align:center;">
                 {randomoji()}
                </p>
                <form action="{action}" method="post">
                {edit_name}
                 <label for="ingredient_name">Zutat:</label>
                 <input type="text"
                        name="ingredient_name"
                        id="ingredient_name"
                        value="{name.capitalize()}"
                        required
                        {"readonly" if name else ""}
                        style="width:100%">
                 <br><br>
                 <label for="ingredient_name">Zutat auf englisch:</label>
                 <input type="text"
                        name="ingredient_name_en"
                        value="{name_en.capitalize()}"
                        id="ingredient_name_en"
                        required
                        style="width:100%"><br><br>
                 <label for="category">Kategorie:</label>
                 <select name="category" id="category" required>
                  <option disabled selected value> -- Kategorie auswählen -- </option>
                  {categories}
                 </select><br>
                 <label>Allergene:</label><br>
                 <select name="allergens" id="allergens"  style="display:inline" multiple size={len(allergens_list())}>
                  {allergens}
                 </select><br><br>
                 <label>Vorbereitung:</label><br>
                 <select name="prep" id="prep"  style="display:inline" multiple size={len(prep_list())}>
                  {prep}
                 </select><br><br>
                 <label>Vorbereitung vortag:</label><br>
                 <select name="prep_daybefore" id="prep_daybefore"  style="display:inline" multiple size={len(prep_daybefore_list())}>
                  {prep_daybefore}
                 </select><br><br>
                 <p><input type="submit" value="Zutat {"editieren" if name else "hinzufügen"}"></p>
                </form>
            """)

    @cherrypy.expose
    def add_ingredient(self, **kwargs):
        return self.ingredient_form("add_ingredient_action") + \
               "<br> <h1>Zutaten</h1> <ul>" + "".join("<li>" +
                    f"""<a href="{self.root}/repertoire/edit_ingredient/?name={urllib.parse.quote(i)}">{i.capitalize().replace("_"," ")}</a>""" + "</li>" for i in ingredients_list()) + "</ul>"

        
    @cherrypy.expose
    def edit_ingredient(self, **kwargs):
        if not kwargs:
            ingredients = ingredients_list()
            return self.selection_page("Zutat zum editieren auswählen", "Editieren!", "", ingredients)
        else:
            ingredient_name = kwargs["name"]
            ingredient = metrodb.search(Query().ingredient == ingredient_name)[0]

            return self.ingredient_form("add_ingredient_action",
                                         ingredient_name,
                                         ingredient["english"],
                                         ingredient["category"],
                                         ingredient["allergens"],
                                         ingredient["prep"],
                                         ingredient["prep_daybefore"])



    @cherrypy.expose
    def add_ingredient_action(self, **kwargs):
        ingredient_name = kwargs["ingredient_name"]
        ingredient_name_en = kwargs["ingredient_name_en"]
        category = kwargs["category"]
        if "allergens" in kwargs.keys():
            if isinstance(kwargs["allergens"], list):
                allergens = [a.lower() for a in kwargs["allergens"]]
            else:
                allergens = [kwargs["allergens"].lower()]
        else:
            allergens = []
        prep = kwargs["prep"]
        prep_daybefore = kwargs["prep_daybefore"]

        edit = "edit" in kwargs.keys()

        if not set(ingredient_name + ingredient_name_en).issubset(allowed.union(set("()"))):
            return self.error_page(f"Zutaten dürfen nur Buchstaben, Zahlen, Punkt und Komma enthalten,\
                                     aber du hast {ingredient_name} und {ingredient_name_en} gesagt.")

        if metrodb.search(Query().ingredient == ingredient_name.lower()) and not edit:
            return self.error_page(f"Die Zutat {ingredient_name.capitalize()} gibt es schon.")
        else:
            metrodb.upsert({"english" : ingredient_name_en.lower(),
                             "category" : category.lower(),
                             "ingredient" : ingredient_name.lower(),
                             "allergens" : allergens,
                             "prep" : prep.lower(),
                             "prep_daybefore" : prep_daybefore.lower()
                           }, Query().ingredient == ingredient_name.lower())

            message = f"Zutat {ingredient_name.capitalize()} " + ("editiert!" if edit else "hinzugefügt!")

            raise cherrypy.HTTPRedirect(f"{self.root}/repertoire?text=" + urllib.parse.quote(message))


    @cherrypy.expose
    def add_recipe(self):
        
        n_ingredients = 15
        
        ingredients = datalist("ingredients",
                               [entry["ingredient"] for entry in metrodb.search(Query().ingredient.exists())])

        materials = datalist("materials",
                             set().union(*[set(entry["materials"]) for entry in self.db.search(Query().materials.exists())]))


        categories = options(c for c in set([entry["category"] for entry in self.db.search(Query().category.exists())]))

        formentries = ""
        for i in range(n_ingredients):
            formentries += f"""
                           <input type="number" step="0.001" name="amount{i}" id="amount{i}">
                           <input type="text" name="ingredient{i}" id="ingredient{i}" list="ingredients">
                           """
        return self.html_body("repertoire",
            f"""<p style="font-size:5em; text-align:center;">
                 {randomoji()}
                </p>
                <form action="add_recipe_action" method="post">
                 <label for="recipe_name">Rezeptname:</label>
                 <input type="text" name="recipe_name" id="recipe_name" required><br><br>
                 <label for="category">Kategorie:</label>
                 <select name="category" id="category" required style="display:inline">
                  <option disabled selected value> -- Kategorie auswählen -- </option>
                  {categories}
                 </select><br><br>
                 <label for="servings">Portionen:</label>
                 <input type="number" name="servings" id="servings" required><br><br>
                 <fieldset>
                  <legend>Menge in kg - Zutaten:</legend>
                  {ingredients}
                  {formentries}
                 </fieldset><br><br>
                 <label for="instructions">Anleitung (optional):</label>
                 <textarea name="instructions" id="instructions" style="height:15em;"></textarea><br>
                 <label>Besonderes Equipment (optional):</label>
                 {materials}
                 <input type="text" name="material1" id="material1" style="width:100%" list="materials"><br>
                 <input type="text" name="material2" id="material2" style="width:100%" list="materials"><br>
                 <input type="text" name="material3" id="material3" style="width:100%" list="materials"><br>
                 <p><input type="submit" value="Rezept hinzufügen"></p>
                </form>
            """)

    @cherrypy.expose
    def add_recipe_action(self, **kwargs):
        n_ingredients = 15
        recipe_name = kwargs["recipe_name"]
        servings = kwargs["servings"]
        category = kwargs["category"]
        instructions = kwargs["instructions"]
        materials = set(kwargs[f"material{n}"] for n in [1,2,3] if kwargs[f"material{n}"])

        if not recipe_name.replace(" ","").isalpha():
            return self.error_page("Nur Buchstaben im Rezeptnamen bitte.")

        if not set(instructions).issubset(allowed):
            return self.error_page("Anleitung darf nur Buchstaben, Zahlen, Punkt und Komma enthalten!")
        if not set("".join(materials)).issubset(allowed):
            return self.error_page("Materialliste darf nur Buchstaben, Zahlen, Punkt und Komma enthalten!")


        ingredient_list = []
        for i in range(n_ingredients):
            ingredient = kwargs[f"ingredient{i}"]
            if ingredient:
                amount = kwargs[f"amount{i}"]
                if not amount:
                    return self.error_page(f"Die Zutat {ingredient} hat keine Mengenangabe.")
                if not set(ingredient).issubset(allowed.union(set("()"))):
                    return self.error_page(f"Zutaten dürfen nur Buchstaben, Zahlen, Punkt und Komma enthalten, aber du hast {ingredient} gesagt.")
                ingredient_list.append((ingredient, float(amount)))

        if ingredient_list:
            ingredients_counter = [("", Counter({ingredient: amount
                                                for (ingredient, amount) in ingredient_list}))]
        else:
            return self.error_page("Dein Rezept hat keine Zutaten.")

        recipe = Recipe(recipe_name, int(servings), 
                        ingredients_counter, instructions, materials, category)

        if self.db.search(Query().name == recipe_name):
            return self.error_page(f"Gibt schon ein Rezept für {recipe_name.capitalize()}, nimm einen anderen Namen.")
        else:
            self.db.insert(recipe_dict(recipe))
            raise cherrypy.HTTPRedirect(f"{self.root}/repertoire?text=" + urllib.parse.quote(f"Rezept {recipe_name.capitalize()} hinzugefügt!"))

    @cherrypy.expose
    def delete_recipe(self):
        return self.selection_page("Rezept zum löschen auswählen",
                                "Wirklich löschen!",
                                "delete_recipe_action",
                                self.recipes()) + f"<br> <h1>Rezepte</h1> {self.recipe_list()}"


    @cherrypy.expose
    def delete_recipe_action(self, **kwargs):
        recipe_name = kwargs["name"]
        self.db.remove(Query().name == recipe_name)
        raise cherrypy.HTTPRedirect(f"{self.root}/repertoire?text=" +
                                      urllib.parse.quote(f"Rezept {recipe_name.capitalize()} gelöscht!"))

    @cherrypy.expose
    def edit_recipe(self, **kwargs):
        if not kwargs:
           return self.selection_page("Rezept zum editieren auswählen",
                                   "Editieren!",
                                   "",
                                   self.recipes()) + f"<br> <h1>Rezepte</h1> {self.recipe_list()}"
        else:
            recipe_name = kwargs["name"]
            recipe = Recipe.from_document(self.db.search(Query().name == recipe_name)[0])

            return self.html_body("repertoire",
                f"""{randomoji_link(".")}
                    <strong>Das Format muss beibehalten werden, sonst geht's nicht.</strong>
                    <div><pre>
10 Portionen

### Zutaten

#### Komponente 1
1 Zwiebeln

#### Komponente 2
200 Knobi

### Anleitung
Komponenten separat pürieren, dann mischen.

### Material
Stabmixer
                    </pre></div>
                    <form action="edit_recipe_action" method="get">
                     <label for="recipe_name"">Rezeptname:</label>
                     <input name="recipe_name" value="{recipe_name}" readonly input type="hidden">
                     <textarea name="recipe" style="height:30em;">{recipe_string(recipe)}</textarea><br>
                     <p><input type="submit" value="Speichern"></p>
                    </form>
                    """)

    @cherrypy.expose
    def edit_recipe_action(self, **kwargs):
        recipe_input = kwargs["recipe"]
        recipe_name = kwargs["recipe_name"]
        try:
            recipe = parser.build_recipe(recipe_input)
        except parser.ParseError as e:
            return self.error_page(f"""<strong>Dein Rezept ist nicht im richtigen Format!</strong><br>
                        Geh zurück und schau es dir nochmal an. Der Fehler:<br>
                        <div>{e}</div>
                     """)

        new_recipe_name = recipe.name
        if not(recipe_name == new_recipe_name) and self.db.search(Query().name == new_recipe_name ):
            return self.error_page(f"Gibt schon ein Rezept für {new_recipe_name.capitalize()}, nimm einen anderen Namen.")
        else:
            self.db.remove(Query().name == recipe_name)
            self.db.insert(recipe_dict(recipe))

            raise cherrypy.HTTPRedirect(f"{self.root}/repertoire?text=" + urllib.parse.quote(f"Rezept {recipe_name.capitalize()} editiert!"))

