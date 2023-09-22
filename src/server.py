import sys
import os, os.path
import cherrypy
from cherrypy.lib import auth_digest
import markdown
import pymdownx
import planner
import parser
from metrodb import metrodb
from random import choice
import urllib.parse
from tinydb import Query
import json
import string

def html_body(css, body):
    return f"""<!DOCTYPE html>
               <html lang="de">
                <head>
                 <meta charset="UTF-8">
                 <meta name="viewport" content="width=device-width, initial-scale=1.0">
                 <link href="/static/css/{css}.css" rel="stylesheet">
                 <link href="/static/pwa_manifest.json" rel="manifest">
                 <link rel="icon" href="/static/favicon.ico">
                 <title>fettnapf3000 Power Kalkulator!</title>
                </head>
                <body>
                 {body}
                 <footer style="margin-top: 5em; text-align: center;">
                   <p>made with &#127814; by team geil</p>
                   <p>contribute on <a href="https://github.com/ooovi/fettnapf3000">github</a></p>
                 </footer>
                </body>
               </html>"""

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

def plan_menu(menu):
    plan = planner.plan(menu)

    extension_configs = { 'pymdownx.tasklist': {'clickable_checkbox': 'True' } }
    plan_html = markdown.markdown(plan,
        extensions=['tables','pymdownx.tasklist'],
        extension_configs=extension_configs)

    return html_body("calculate",
        f"""<p style="font-size:5em; text-align:center;">
             <a onclick="window.print();" style="text-decoration: none">
              {randomoji()}
             </a>
            </p>
            {plan_html}
            <hr>
            <div style="text-align: center;">
             Rezepte können Spuren von Tipp- und Denkfehlern enthalten.
             Wenn du welche findest, <a href="https://github.com/ooovi/fettnapf3000">sag Bescheid</a>!
            </div>
        """)


def error_page(error):
    return html_body("menu",
        f"""<p style="font-size:7em; text-align:center;">
             <a href="#" onclick="history.back()" style="text-decoration: none">
             {randomoji()}
             </a></p>
             {error}
        """)


def recipe_list(user):
    recipes = [os.path.splitext(recipe)[0].capitalize() for recipe in os.listdir(f"../recipes/{user}")]
    recipes.sort()
    return f"""<ul style="columns:2; -webkit-columns:2; -moz-columns:2; list-style-type:none;">
                {"".join("<li>" + recipe + "</li>" for recipe in recipes)}
               </ul>"""

class RecipePage:
    def __init__(self, user="team"):
        self.user = user
        if not user == "team":
            self.root = "/" + user
        else:
            self.root = ""

    @cherrypy.expose
    def index(self):
        return html_body("recipes",
        f"""{randomoji_link("menu")}
            <strong>Stelle Anzahl Portionen pro Gericht ein und drück auf Kalkulation!</strong>
            <br> Speicher danach den Link, um deine Kalkulation zu teilen, oder drucke die Seite aus.
            <br> Falls du viele verschiedene Gerichte planst könnte dich unser <a href="./menu">Menü-Planer</a> interessieren!
            <br> Falls du eine Koche organisieren willst, lad dir den <a href="https://food4action.noblogs.org/fettnapf/">Fettnapf</a> runter, das ultimative SoKü-Handbuch unserer Herzen.<br>
            {self.create_recipes_form()}
        """)

    def create_recipes_form(self):
        recipes = os.listdir(f"../recipes/{self.user}")
        recipes.sort()
        html_string = f" <form action=\"{self.root}/request\" method=\"get\">"
        for recipe in recipes:
            html_string += f"""<p>
                <label for="{recipe}">
                 {os.path.splitext(recipe)[0].capitalize().replace("_"," ")}:&ensp;
                </label>
                <input type="number" name="{recipe}" id="{recipe}"><br>
                </p>"""
        html_string += """<p><input type="submit" value="Kalkulation"></p></form>"""
        return html_string

class MenuPage:
    def __init__(self, user="team"):
        self.user = user
        if not user == "team":
            self.root = "/" + user
        else:
            self.root = ""

    @cherrypy.expose
    def index(self):
        return html_body("menu",
            f"""{randomoji_link(self.root + "/")}
                <strong>Gib ein Menü in diesem Format an:</strong>
                <div><pre>
### Montag
1 Supershake

### Dienstag
1 Supershake

### Rest der Woche
100 Kaffe
100 Kürbisschnecken
                </pre></div>
                Die Namen der Gerichte müssen genau der Liste unten entsprechen!<br>
                Drück auf Kalkulation. Speicher danach den Link, um deine Kalkulation zu teilen, oder drucke die Seite aus.
                <form action="{self.root}/calculate_menu" method="get" >
                 <textarea name="menu"></textarea><br>
                 <p><input type="submit" value="Kalkulation"></p>
                </form>
               <h1>Rezepte</h1>
               {recipe_list(self.user)}
            """)

class CalculateMenuPage:
    def __init__(self, user="team"):
        self.user = user

    @cherrypy.expose
    def index(self, **kwargs):
        menu_md = kwargs.get("menu")
        try:
            menu_list = parser.parse_menu(menu_md)
        except parser.ParseError as e:
            return error_page(f"""<strong>Dein Menü ist nicht im richtigen Format!</strong><br>
                        Geh zurück und schau es dir nochmal an. Der Fehler:<br>
                        <div>{e}</div>
                     """)
        menu = {}
        for (category, recipe_name, n_servings) in menu_list:
             recipe_file = f"../recipes/{self.user}/" + recipe_name + ".txt"
             try:
                 recipe = parser.parse_recipe(recipe_file)
             except IOError as e:
                 return error_page(f"""<strong>Das Rezept {recipe_name.capitalize().replace("_"," ")} steht nicht in der Liste!</strong><br>
                        Geh zurück und schau es dir nochmal an.
                     """)
             if category in menu:
                 menu[category].append((recipe, n_servings))
             else:
                 menu[category] = [(recipe, n_servings)]
        return plan_menu(menu)



class RequestPage:
    def __init__(self, user="team"):
        self.user = user
        if not user == "team":
            self.root = "/" + user
        else:
            self.root = ""

    @cherrypy.expose
    def index(self, **kwargs):
        # clean empty form entries from url
        clean_request = { (r,n) for (r,n) in kwargs.items() if n }
        raise cherrypy.HTTPRedirect(
            f"{self.root}/calculate/?" + '&'.join(f"{urllib.parse.quote(r)}={n}" for (r,n) in clean_request)
        )

class CalculatePage:
    def __init__(self, user="team"):
        self.user = user
        if not user == "team":
            self.root = user
        else:
            self.root = ""

    @cherrypy.expose
    def index(self, **kwargs):
        if not kwargs:
            raise cherrypy.HTTPRedirect(f"/{self.root}")

        menu = {}
        for (recipe_name, n) in kwargs.items():
            if n:
                recipe = parser.parse_recipe(f"../recipes/{self.user}/" + recipe_name)
                n_servings = int(n)
                if "Rezepte" in menu:
                     menu["Rezepte"].append((recipe, n_servings))
                else:
                     menu["Rezepte"] = [(recipe, n_servings)]

        return plan_menu(menu)

class RepertoirePage:
    @cherrypy.expose
    def index(self, **kwargs):
        user = cherrypy.request.login
        text = ""
        if kwargs:
            text = kwargs["text"]
        return html_body("repertoire",
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
                <form action="../{user}">
                 <p><input type="submit" value="Kalkulation"></p>
                </form>
                 <br>
                <h1>Rezepte</h1>
                {recipe_list(user)}
            """)

class DeleteRecipePage:
    @cherrypy.expose
    def index(self):
        user = cherrypy.request.login
        recipes = [os.path.splitext(recipe)[0].capitalize() for recipe in os.listdir(f"../recipes/{user}")]
        recipes.sort()
        return html_body("repertoire",
            f"""{randomoji_link(".")}
                <form action="delete_recipe" method="post">
                 <select name="recipe_name" id="select" required style="width:100%">
                  <option disabled selected value> -- Rezept zum löschen auswählen -- </option>
                  {"".join("<option>" + recipe + "</option>" for recipe in recipes)}
                 </select>
                 <p><input type="submit" value="Wirklich löschen!"></p>
                 </form>
                <form action="/repertoire">
                 <p><input type="submit" value="Doch nicht."></p>
                </form>
                 <br>
                <h1>Rezepte</h1>
                {recipe_list(user)}
            """)


    @cherrypy.expose
    def delete_recipe(self, **kwargs):
        recipe_name = kwargs["recipe_name"]
        recipe_filename = recipe_name.replace(" ","_")
        recipe_path = f"../recipes/{cherrypy.request.login}/{recipe_filename.lower()}.txt"
        os.remove(recipe_path)
        raise cherrypy.HTTPRedirect("/repertoire?text=" + urllib.parse.quote(f"Rezept {recipe_name} gelöscht!"))
    
class AddRecipePage:
    n_ingredients = 15

    @cherrypy.expose
    def index(self):
        ingredients = [entry["ingredient"] for entry in metrodb.search(Query().ingredient.exists())]
        datalist = "<datalist id=\"ingredients\">\n"
        for ingredient in ingredients:
            datalist += f"<option value=\"{ingredient.capitalize()}\">{ingredient.capitalize()}</option>\n"
        datalist += "</datalist>"

        formentries = ""
        for i in range(self.n_ingredients):
            formentries += f"""
                           <input type="number" step="0.001" name="amount{i}" id="amount{i}">
                           <input type="text" name="ingredient{i}" id="ingredient{i}" list="ingredients">
                           """
        return html_body("repertoire",
            f"""<p style="font-size:5em; text-align:center;">
                 {randomoji()}
                </p>
                <form action="add_recipe" method="post">
                 <label for="recipe_name">Rezeptname:</label>
                 <input type="text" name="recipe_name" id="recipe_name"><br><br>
                 <label for="servings">Portionen:</label>
                 <input type="number" name="servings" id="servings"><br><br>
                 <fieldset>
                  <legend>Menge in kg - Zutaten:</legend>
                  {datalist}
                  {formentries}
                 </fieldset><br><br>
                 <label for="instructions">Anleitung (optional):</label>
                 <textarea name="instructions" id="instructions" style="height:15em"></textarea><br>
                 <label for="materials">Besonderes Equipment (optional):</label>
                 <textarea name="materials" id="materials"></textarea><br><br>
                 <p><input type="submit" value="Rezept hinzufügen"></p>
                </form>
            """)

    @cherrypy.expose
    def add_recipe(self, **kwargs):
        recipe_name = kwargs["recipe_name"]
        servings = kwargs["servings"]
        instructions = kwargs["instructions"]
        materials = kwargs["materials"]

        if recipe_name == "":
            return error_page("Bitte gib deinem Rezept einen Namen.")
        if not recipe_name.replace(" ","").isalpha():
            return error_page("Nur Buchstaben im Rezeptnamen bitte.")
        if servings == "":
            return error_page("Bitte gib die Anzahl Portionen an.")

        allowed = set(string.ascii_lowercase + string.ascii_uppercase + string.digits + ".,äöüÄÖÜß ")
        if not set(instructions).issubset(allowed):
            return error_page("Anleitung darf nur Buchstaben, Zahlen, Punkt und Komma enthalten!")
        if not set(materials).issubset(allowed):
            return error_page("Materialliste darf nur Buchstaben, Zahlen, Punkt und Komma enthalten!")

        recipe = f"## {recipe_name.capitalize()}\n"
        recipe += f"{servings} Portionen\n\n"
        recipe += "### Zutaten\n"

        ingredient_list = ""

        for i in range(self.n_ingredients):
            ingredient = kwargs[f"ingredient{i}"]
            if ingredient:
                amount = kwargs[f"amount{i}"]
                if not amount:
                    return error_page(f"Die Zutat {ingredient} hat keine Mengenangabe.")
                if not set(ingredient).issubset(allowed.union(set("()"))):
                    return error_page(f"Zutaten dürfen nur Buchstaben, Zahlen, Punkt und Komma enthalten, aber du hast {ingredient} gesagt.")
                ingredient_list += f"{amount} {ingredient}\n"

        if ingredient_list:
            recipe += ingredient_list
        else:
            return error_page("Dein Rezept hat keine Zutaten.")

        if instructions:
            recipe += f"\n### Anleitung\n{instructions}\n"

        if materials:
            recipe += f"\n### Material\n{materials}\n"

        user = cherrypy.request.login
        recipe_filename = recipe_name.replace(" ","_")
        recipe_path = f"../recipes/{user}/{recipe_filename.lower()}.txt"
        if os.path.isfile(recipe_path):
            return error_page(f"Gibt schon ein Rezept für {recipe_name}, nimm einen anderen Namen.")

        file = open(recipe_path, "a")
        file.write(recipe)
        file.close()
        
        raise cherrypy.HTTPRedirect("/repertoire?text=" + urllib.parse.quote(f"Rezept {recipe_name} hinzugefügt!"))

USERS = json.load(open("users.txt"))
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
            'tools.auth_digest.get_ha1': auth_digest.get_ha1_dict_plain(USERS),
            'tools.auth_digest.key': KEY,
            'tools.auth_digest.accept_charset': 'UTF-8',
         }
    }

    root = RecipePage()
    root.team = RecipePage("team")
    root.request = RequestPage()
    root.menu = MenuPage()
    root.calculate_menu = CalculateMenuPage()
    root.calculate = CalculatePage()
    
    root.repertoire = RepertoirePage()
    root.repertoire.add = AddRecipePage()
    root.repertoire.delete = DeleteRecipePage()
    
    root.food4action = RecipePage("food4action")
    root.food4action.request = RequestPage("food4action")
    root.food4action.menu = MenuPage("food4action")
    root.food4action.calculate_menu = CalculateMenuPage("food4action")
    root.food4action.calculate = CalculatePage("food4action")

    cherrypy.quickstart(root, config = conf)