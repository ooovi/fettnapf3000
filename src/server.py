import sys
import os
import urllib.parse
import json
import string
from random import choice
from collections import Counter

from tinydb import Query, TinyDB
import cherrypy
import markdown
import pymdownx

import planner
import parser
from recipe import Recipe, recipe_string,recipe_dict

db = {"team": TinyDB(f'../../fettnapf3000recipes/team_recipes.json', indent=2),
      "food4action": TinyDB(f'../../fettnapf3000recipes/food4action_recipes.json', indent=2),
      "cutiemeow": TinyDB(f'../../fettnapf3000recipes/cutiemeow_recipes.json', indent=2)}

metrodb = TinyDB('../../fettnapf3000recipes/metrodb.json', indent=2)


class FettnapfPage:
    def __init__(self, user="team"):
        self.user = user
        if not user == "team":
            self.root = "/" + user
        else:
            self.root = ""

    def html_body(self, css, body, add_footer=True):
        footer = ""
        if add_footer:
            footer = f"""
                     <hr>
                     <nav style="text-align:center;">
                      <a href="{self.root}/">Rezeptplaner</a> |
                      <a href="{self.root}/menu/">Menüplaner</a> |
                      <a href="{self.root}/repertoire/">Repertoire verwalten</a>
                    </nav>
                     <footer style="margin-top: 3em; text-align: center;">
                       <p>made with &#127814; by team geil</p>
                       <p>contribute on <a href="https://github.com/ooovi/fettnapf3000">github</a></p>
                       <p>mail an fettnapf3000 ät posteo punkt de</p>
                     </footer>
            """

        return f"""<!DOCTYPE html>
                   <html lang="de">
                    <head>
                     <meta charset="UTF-8">
                     <meta name="viewport" content="width=device-width, initial-scale=1.0">
                     <link href="/static/css/{css}.css" rel="stylesheet">
                     <link href="/static/pwa_manifest.json" rel="manifest">
                     <link href="/static/favicon.ico" rel="icon">
                     <title>fettnapf3000 Power Kalkulator!</title>
                    </head>
                    <body>
                     {body}
                     {footer}
                    </body>
                   </html>"""

    def error_page(self, error):
        return self.html_body("menu",
            f"""<p style="font-size:5em; text-align:center;">
                 <a href="#" onclick="history.back()" style="text-decoration: none">
                 {randomoji()}
                 </a></p>
                 {error}
            """)

    def recipes(self):
        recipes = [recipe['name'] for recipe in db[self.user].search(Query().name.exists())]
        recipes.sort()
        return recipes

    def recipes_cat(self):
        recipes = {}
        for recipe in db[self.user].search(Query().name.exists()):
            if 'category' in recipe:
                cat = recipe['category']
            else:
                cat = "misc"
            recipes.setdefault(cat, []).append(recipe['name'])
        return recipes

    def recipe_list(self, edit=False):
        html_str = """<dl style="list-style-type:none;">"""
        for (cat, recipes) in sorted(self.recipes_cat().items()):
            recipes.sort()
            recipe_links = []
            for recipe in recipes:
                if edit:
                    link = f"repertoire/edit/?recipe_name={urllib.parse.quote(recipe)}"
                else:
                    link = f"calculate?{urllib.parse.quote(recipe)}=10"
                recipe_links.append(f"""<a href="{self.root}/{link}">{recipe.capitalize().replace("_"," ")}</a>""")
            html_str += f"<dt style=\"font-size:1.2em;padding-top:0.5em\"><strong>{cat.capitalize()}</strong></dt>"
            html_str += "".join("<dd>" + recipe + "</dd>" for recipe in recipe_links)
        return html_str + "</dl>"

    def recipe_options(self):
        return "".join(f"<option value=\"{recipe}\"> {recipe.capitalize()} </option>" for recipe in self.recipes())

    def plan_menu(self, menu_md):
        try:
            menu_list = parser.parse_menu(menu_md)
        except parser.ParseError as e:
            return self.error_page(f"""<strong>Dein Menü ist nicht im richtigen Format!</strong><br>
                        Geh zurück und schau es dir nochmal an. Der Fehler:<br>
                        <div>{e}</div>
                     """)
        menu = {}
        for (category, recipe_name, n_servings) in menu_list:
             recipe_entries = db[self.user].search(Query().name == recipe_name)
             if recipe_entries:
                 recipe = Recipe.from_document(recipe_entries[0])
             else:
                 return self.error_page(f"""<strong>Das Rezept {recipe_name.capitalize().replace("_"," ")} steht nicht in der Liste!</strong><br>
                        Geh zurück und schau es dir nochmal an.
                     """)
             if category in menu:
                 menu[category].append((recipe, n_servings))
             else:
                 menu[category] = [(recipe, n_servings)]

        plan = planner.plan(menu)
    
        extension_configs = { 'pymdownx.tasklist': {'clickable_checkbox': 'True' } }
        plan_html = markdown.markdown(plan,
            extensions=['tables','pymdownx.tasklist'],
            extension_configs=extension_configs)

        moji = randomoji_control(self.root + "/menu/?menu=" + urllib.parse.quote(menu_md), "editieren")

        return self.html_body("calculate",
            f"""{moji}
                {plan_html}
                <hr>
                <div style="text-align: center;">
                 Rezepte können Spuren von Tipp- und Denkfehlern enthalten.
                 Wenn du welche findest, mail an fettnapf3000 ät posteo punkt de</a>!
                </div>
            """, False)


def randomoji():
    return choice(["&#127814;",
                   "&#127798;",
                   "&#127826;",
                   "&#127825;",
                   "&#127853;",
                   "&#129373;",
                   "&#129361;",
                   "&#129473;",
                   "&#129375;",
                   "&#127817;",
                   "&#127849;",
                   "&#127820;",
                   "&#127805;",
                   "&#127852;",
                   "&#127815;",
                   "&#127822;",
                   "&#127789;"])

def randomoji_link(ref):
    return f"""
           <p style="font-size:5em; text-align:center;">
            <a href="{ref}" style="text-decoration: none">
             {randomoji()}
            </a></p>"""

def randomoji_control(ref, control):
    return f"""
           <p style="font-size:5em; text-align:center;">
            <a href="{ref}" style="text-decoration: none">
             <span class="emoji">{randomoji()}</span>
             <span class="control">{control}</span>
            </a></p>"""

def options(input_list):
    return "".join(f"<option value=\"{input}\"> {input.capitalize()} </option>" for input in input_list)

def datalist(id, input_list, selected = []):
    datalist = "<datalist id=\"" + id + "\">\n"
    for input in input_list:
        s = "selected" if input in selected else ""
        datalist += f"<option {s} value=\"{input.capitalize()}\">{input.capitalize()}</option>\n"
    datalist += "</datalist>"
    return datalist

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

class RecipePage(FettnapfPage):
    @cherrypy.expose
    def index(self):
        return self.html_body("recipes",
        f"""{randomoji_link("menu")}
            <strong>Stelle Anzahl Portionen pro Gericht ein und drück auf Kalkulation!</strong>
            <br> Speicher danach den Link, um deine Kalkulation zu teilen, oder drucke die Seite aus.
            <br> Falls du viele verschiedene Gerichte planst könnte dich unser <a href="./menu">Menü-Planer</a> interessieren!
            <br> Falls du eine Koche organisieren willst, lad dir den <a href="https://food4action.noblogs.org/fettnapf/">Fettnapf</a> runter, das ultimative SoKü-Handbuch unserer Herzen.<br>
            {self.create_recipes_form()}
        """)

    def create_recipes_form(self):
        html_string = f" <form action=\"{self.root}/request\" method=\"get\">"
        for (cat, recipes) in self.recipes_cat().items():
            html_string += f"<h2>{cat.capitalize()}</h2>"
            for recipe in recipes:
                html_string += f"""<p>
                <label for="{recipe}">
                 {recipe.capitalize()}:&ensp;
                </label>
                <input type="number" name="{recipe}" id="{recipe}"><br>
                </p>"""
        html_string += """<p><input type="submit" value="Kalkulation"></p></form>"""
        return html_string

    @cherrypy.expose
    def menu(self, **kwargs):
        menu = ""
        if kwargs:
            menu = kwargs.get("menu")

        return self.html_body("menu",
            f"""{randomoji_link(self.root + "/")}
                <strong>Gib ein Menü in diesem Format an:</strong>
                <div><pre>
### Montag
1 Super shake

### Dienstag
1 Super shake

### Rest der Woche
100 Kaffe
100 Kürbisschnecken mit orangenbutter
                </pre></div>
                Die Namen der Gerichte müssen genau der Liste unten entsprechen!<br>
                Drück auf Kalkulation. Speicher danach den Link, um deine Kalkulation zu teilen, oder drucke die Seite aus.
                <form action="{self.root}/calculate_menu" method="get" >
                 <textarea name="menu">{menu}</textarea><br>
                 <p><input type="submit" value="Kalkulation"></p>
                </form>
               <h1>Rezepte</h1>
               {self.recipe_list()}
            """)
    
    @cherrypy.expose
    def calculate_menu(self, **kwargs):
        return self.plan_menu(kwargs.get("menu"))

    @cherrypy.expose
    def request(self, **kwargs):
        # clean empty form entries from url
        clean_request = { (r,n) for (r,n) in kwargs.items() if n }
        raise cherrypy.HTTPRedirect(
            f"{self.root}/calculate/?" + '&'.join(f"{urllib.parse.quote(r)}={n}" for (r,n) in clean_request)
        )

    @cherrypy.expose
    def calculate(self, **kwargs):
        if not kwargs:
            raise cherrypy.HTTPRedirect(f"/{self.root}")

        return self.plan_menu("### Rezepte\n" + "\n".join(f"{n} {recipe_name}" for (recipe_name, n) in kwargs.items()))

class RepertoirePage(FettnapfPage):
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
                <form action="add">
                 <p><input type="submit" value="Neues Rezept"></p>
                </form>
                <form action="delete" method="post">
                 <p><input type="submit" value="Rezept löschen"></p>
                </form>
                <form action="edit" method="post">
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
    def delete(self):
        return self.html_body("repertoire",
            f"""{randomoji_link(".")}
                <form action="delete_recipe" method="post">
                 <select name="recipe_name" id="select" required style="width:100%">
                  <option disabled selected value> -- Rezept zum löschen auswählen -- </option>
                  {options(self.recipes())}
                 </select>
                 <p><input type="submit" value="Wirklich löschen!"></p>
                 </form>
                <form action="{self.root}/repertoire">
                 <p><input type="submit" value="Doch nicht."></p>
                </form>
                 <br>
                <h1>Rezepte</h1>
                {self.recipe_list()}
            """)


    @cherrypy.expose
    def delete_recipe(self, **kwargs):
        recipe_name = kwargs["recipe_name"]
        db[self.user].remove(Query().name == recipe_name)
        raise cherrypy.HTTPRedirect(f"{self.root}/repertoire?text=" + urllib.parse.quote(f"Rezept {recipe_name.capitalize()} gelöscht!"))
    
    @cherrypy.expose
    def delete_ingredient(self):
        return self.html_body("repertoire",
            f"""{randomoji_link(".")}
                <form action="delete_ingredient_action" method="post">
                 <select name="ingredient_name" id="select" required style="width:100%">
                  <option disabled selected value> -- Zutat zum löschen auswählen -- </option>
                  {options(ingredients_list())}
                 </select>
                 <p><input type="submit" value="Wirklich löschen!"></p>
                 </form>
                <form action="{self.root}/repertoire">
                 <p><input type="submit" value="Doch nicht."></p>
                </form>
            """)

    @cherrypy.expose
    def delete_ingredient_action(self, **kwargs):
        ingredient_name = kwargs["ingredient_name"]
        metrodb.remove(Query().ingredient == ingredient_name)
        raise cherrypy.HTTPRedirect(f"{self.root}/repertoire?text=" + urllib.parse.quote(f"Zutat {ingredient_name.capitalize()} gelöscht!"))

    @cherrypy.expose
    def add_ingredient(self, **kwargs):
        
        allergens = datalist("allergens", allergens_list())

        categories = datalist("categories", categories_list())

        return self.html_body("repertoire",
            f"""<p style="font-size:5em; text-align:center;">
                 {randomoji()}
                </p>
                <form action="add_ingredient_action" method="post">
                 <label for="ingredient_name">Zutat:</label>
                 <input type="text" name="ingredient_name" id="ingredient_name" required style="width:100%"><br><br>
                 <label for="ingredient_name">Zutat auf englisch:</label>
                 <input type="text" name="ingredient_name_en" id="ingredient_name_en" required style="width:100%"><br><br>
                 <label for="category">Kategorie:</label>
                 <select name="category" id="category" required>
                  <option disabled selected value> -- Kategorie auswählen -- </option>
                  {categories}
                 </select><br>
                 <label>Allergene:</label><br>
                 <select name="allergens" id="allergens"  style="display:inline" multiple size={len(allergens_list())}>
                  {allergens}
                 </select><br><br>
                 <p><input type="submit" value="Zutat hinzufügen"></p>
                </form>
            """)

    @cherrypy.expose
    def edit_ingredient(self, **kwargs):
        if not kwargs:
            ingredients = ingredients_list()
                       
            return self.html_body("repertoire",
               f"""{randomoji_link(".")}
                   <form action="" method="post">
                    <select name="ingredient_name" id="select" required style="width:100%">
                     <option disabled selected value> -- Zutat zum editieren auswählen -- </option>
                     {"".join(f"<option value=\"{ingredient}\"> {ingredient.capitalize()} </option>" for ingredient in ingredients)}
                    </select>
                    <p><input type="submit" value="Editieren!"></p>
                    </form>
                   <form action="{self.root}/repertoire">
                    <p><input type="submit" value="Doch nicht."></p>
                   </form>
                    <br>
               """)
        else:
            ingredient_name = kwargs["ingredient_name"]
            ingredient = metrodb.search(Query().ingredient == ingredient_name)[0]

            allergens = datalist("allergens", allergens_list(), ingredient['allergens'])
            categories = datalist("categories",
                                  categories_list(),
                                  ingredient['category'])
        

            formentries = f"""
                 <select name="allergens" id="allergens"  style="display:inline" multiple size={len(allergens_list())}>
                  {allergens}
                 </select><br><br> """
                
            return self.html_body("repertoire",
                f"""<p style="font-size:5em; text-align:center;">
                     {randomoji()}
                    </p>
                    <form action="add_ingredient_action" method="post">
                     <input type="hidden" id="edit" value="aaa" name="edit">
                     <label for="ingredient_name">Zutat:</label>
                     <input name="ingredient_name" value="{ingredient_name.capitalize()}" readonly input style="width:100%"><br><br>
                     <label for="ingredient_name">auf Englisch:</label>
                     <input type="text" name="ingredient_name_en" id="ingredient_name_en" value="{ingredient['english'].capitalize()}" required style="width:100%"><br><br>
                     <label for="category">Kategorie:</label>
                     <select name="category" id="category" required>
                      {categories}
                     </select><br>
                     <label>Allergene:</label><br>
                     {formentries}
                     <p><input type="submit" value="Zutat editieren"></p>
                    </form>
                """)


    @cherrypy.expose
    def add_ingredient_action(self, **kwargs):
        print(kwargs)
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
        edit = "edit" in kwargs.keys()

        allowed = set(string.ascii_lowercase + string.ascii_uppercase + string.digits + ".,äöüÄÖÜß !?€-/\"\'\n\r")
        if not set(ingredient_name + ingredient_name_en).issubset(allowed.union(set("()"))):
            return self.error_page(f"Zutaten dürfen nur Buchstaben, Zahlen, Punkt und Komma enthalten,\
                                     aber du hast {ingredient_name} und {ingredient_name_en} gesagt.")

        if metrodb.search(Query().ingredient == ingredient_name.lower()) and not edit:
            return self.error_page(f"Die Zutat {ingredient_name.capitalize()} gibt es schon.")
        else:
            metrodb.upsert({"english" : ingredient_name_en.lower(),
                             "category" : category.lower(),
                             "ingredient" : ingredient_name.lower(),
                             "allergens" : allergens
                           }, Query().ingredient == ingredient_name.lower())

            message = f"Zutat {ingredient_name.capitalize()} " + ("editiert!" if edit else "hinzugefügt!")

            raise cherrypy.HTTPRedirect(f"{self.root}/repertoire?text=" + urllib.parse.quote(message))


    @cherrypy.expose
    def add(self):
        
        n_ingredients = 15
        
        ingredients = datalist("ingredients",
                               [entry["ingredient"] for entry in metrodb.search(Query().ingredient.exists())])

        materials = datalist("materials",
                             set().union(*[set(entry["materials"]) for entry in db[self.user].search(Query().materials.exists())]))

        categories = "".join(set("<option value=\"" 
                                 + cat["category"] 
                                 + "\">" 
                                 + cat["category"].capitalize() 
                                 + " </option>" 
                             for cat in db[self.user].search(Query().category.exists())))

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
                <form action="add_recipe" method="post">
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
    def add_recipe(self, **kwargs):
        n_ingredients = 15
        recipe_name = kwargs["recipe_name"]
        servings = kwargs["servings"]
        category = kwargs["category"]
        instructions = kwargs["instructions"]
        materials = set(kwargs[f"material{n}"] for n in [1,2,3] if kwargs[f"material{n}"])

        if not recipe_name.replace(" ","").isalpha():
            return self.error_page("Nur Buchstaben im Rezeptnamen bitte.")

        allowed = set(string.ascii_lowercase + string.ascii_uppercase + string.digits + ".,äöüÄÖÜß !?€-/\"\'\n\r")
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

        if db[self.user].search(Query().name == recipe_name):
            return self.error_page(f"Gibt schon ein Rezept für {recipe_name.capitalize()}, nimm einen anderen Namen.")
        else:
            db[self.user].insert(recipe_dict(recipe))
            raise cherrypy.HTTPRedirect(f"{self.root}/repertoire?text=" + urllib.parse.quote(f"Rezept {recipe_name.capitalize()} hinzugefügt!"))

    @cherrypy.expose
    def edit(self, **kwargs):
        if not kwargs:
           return self.html_body("repertoire",
               f"""{randomoji_link(".")}
                   <form action="" method="post">
                    <select name="recipe_name" id="select" required style="width:100%">
                     <option disabled selected value> -- Rezept zum editieren auswählen -- </option>
                     {options(self.recipes())}
                    </select>
                    <p><input type="submit" value="Editieren!"></p>
                    </form>
                   <form action="{self.root}/repertoire">
                    <p><input type="submit" value="Doch nicht."></p>
                   </form>
                    <br>
                   <h1>Rezepte</h1>
                   {self.recipe_list()}
               """)
        else:
            recipe_name = kwargs["recipe_name"]
            recipe = Recipe.from_document(db[self.user].search(Query().name == recipe_name)[0])

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
                    <form action="edit_recipe" method="get">
                     <label for="recipe_name"">Rezeptname:</label>
                     <input name="recipe_name" value="{recipe_name}" readonly input type="hidden">
                     <textarea name="recipe" style="height:30em;">{recipe_string(recipe)}</textarea><br>
                     <p><input type="submit" value="Speichern"></p>
                    </form>
                    """)

    @cherrypy.expose
    def edit_recipe(self, **kwargs):
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
        if not(recipe_name == new_recipe_name) and db[self.user].search(Query().name == new_recipe_name ):
            return self.error_page(f"Gibt schon ein Rezept für {new_recipe_name.capitalize()}, nimm einen anderen Namen.")
        else:
            db[self.user].remove(Query().name == recipe_name)
            db[self.user].insert(recipe_dict(recipe))

            raise cherrypy.HTTPRedirect(f"{self.root}/repertoire?text=" + urllib.parse.quote(f"Rezept {recipe_name.capitalize()} editiert!"))


TEAM_USERS = json.load(open("users.txt"))
F4A_USERS = json.load(open("f4a_users.txt"))
CUTIEMEOW_USERS = json.load(open("cutiemeow_users.txt"))
KEY = open("key.txt").read()

if __name__ == '__main__':
    if len(sys.argv) == 3:
        cherrypy.config.update({'server.socket_host': sys.argv[1],
                                'server.socket_port': int(sys.argv[2]),
                               })
    if len(sys.argv) == 2:
        cherrypy.config.update({'server.socket_port': int(sys.argv[1])})
    conf = {
        '/': {
            'tools.sessions.on': False,
            'tools.staticdir.root': os.path.abspath(os.getcwd())
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './public'
        },
        '/repertoire': {
            'tools.auth_digest.on': True,
            'tools.auth_digest.realm': 'localhost',
            'tools.auth_digest.get_ha1': cherrypy.lib.auth_digest.get_ha1_dict_plain(TEAM_USERS),
            'tools.auth_digest.key': KEY,
            'tools.auth_digest.accept_charset': 'UTF-8',
         },
         '/food4action/repertoire': {
            'tools.auth_digest.on': True,
            'tools.auth_digest.realm': 'localhost',
            'tools.auth_digest.get_ha1': cherrypy.lib.auth_digest.get_ha1_dict_plain(F4A_USERS),
            'tools.auth_digest.key': KEY,
            'tools.auth_digest.accept_charset': 'UTF-8',
         },
         '/cutiemeow/repertoire': {
            'tools.auth_digest.on': True,
            'tools.auth_digest.realm': 'localhost',
            'tools.auth_digest.get_ha1': cherrypy.lib.auth_digest.get_ha1_dict_plain(CUTIEMEOW_USERS),
            'tools.auth_digest.key': KEY,
            'tools.auth_digest.accept_charset': 'UTF-8',
         }
    }

    root = RecipePage()
    root.team = RecipePage("team")
    root.repertoire = RepertoirePage()

    root.food4action = RecipePage("food4action")
    root.food4action.repertoire = RepertoirePage("food4action")

    root.cutiemeow = RecipePage("cutiemeow")
    root.cutiemeow.repertoire = RepertoirePage("cutiemeow")

    cherrypy.quickstart(root, config = conf)
