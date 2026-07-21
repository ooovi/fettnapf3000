import markdown
from tinydb import Query, TinyDB
import urllib.parse
import pymdownx

import parser
import planner
from recipe import Recipe
from utils import randomoji, randomoji_control

urldb = TinyDB('requests.json', indent=2)

class FettnapfPage:
    def __init__(self, db, user="team"):
        self.db = db[user]
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
        recipes = [recipe['name'] for recipe in self.db.search(Query().name.exists())]
        recipes.sort()
        return recipes

    def recipes_cat(self):
        recipes = {}
        for recipe in self.db.search(Query().name.exists()):
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
                    link = f"repertoire/edit_recipe?name={urllib.parse.quote(recipe)}"
                else:
                    link = f"calculate?{urllib.parse.quote(recipe)}=10"
                recipe_links.append(f"""<a href="{self.root}/{link}">{recipe.capitalize().replace("_"," ")}</a>""")
            html_str += f"<dt style=\"font-size:1.2em;padding-top:0.5em\"><strong>{cat.capitalize()}</strong></dt>"
            html_str += "".join("<dd>" + recipe + "</dd>" for recipe in recipe_links)
        return html_str + "</dl>"

    def menu_html(self, menu_md):
        try:
            menu_list = parser.parse_menu(menu_md)
        except parser.ParseError as e:
            raise Exception(self.error_page(f"""<strong>Dein Menü ist nicht im richtigen Format!</strong><br>
                        Geh zurück und schau es dir nochmal an. Der Fehler:<br>
                        <div>{e}</div>"""))
        menu = {}
        for (day, (category, recipe_name, n_servings)) in menu_list:
            recipe_entries = self.db.search(Query().name == recipe_name)
            if recipe_entries:
                recipe = Recipe.from_document(recipe_entries[0])
            else:
                raise Exception(self.error_page(f"""<strong>Das Rezept {recipe_name.capitalize().replace("_"," ")} steht nicht in der Liste!</strong><br>
                    geh zurück und schau es dir nochmal an."""))
            if day in menu:
                if category in menu[day]:
                    menu[day][category].append((recipe, n_servings))
                else:
                    menu[day][category] = [(recipe, n_servings)]
            else:
                menu[day] = {category : [(recipe, n_servings)]}

        plan = planner.plan(menu)

        extension_configs = { 'pymdownx.tasklist': {'clickable_checkbox': 'True' } }

        return markdown.markdown(plan,
            extensions=['tables','pymdownx.tasklist'],
            extension_configs=extension_configs)

    def store_menu(self, menu_md, id, readonly = ''):
        if urldb.search(Query().id == id) and urldb.search(Query().id == id)[0].get("readonly"): #do not edit readonly menus
            raise Exception(self.error_page(f"""<strong>Die Kalkulation {id} ist read-only und darf nicht editiert werden! Wähle einen anderen Namen.</strong><br>"""))

        html = self.menu_html(menu_md)

        # store the menu and html in the database
        urldb.upsert({'id' : id, 'menu_md' : menu_md, 'html' : html, 'readonly' : True if readonly else False}, Query().id == id)

    def plan_stored(self, id):
        entry = urldb.search(Query().id == id)
        if not entry:
            return self.error_page(f"""<strong>Die Kalkulation {id} existiert nicht.</strong>""")

        moji = randomoji_control(self.root + "/menu?id=" + urllib.parse.quote(id), "editieren")
        return self.html_body("calculate",
            f"""{moji}
                <p style="font-size:2em; text-align:center;"> {id} </p>
                {entry[0].get("html")}
                <hr>
                <div style="text-align: center;">
                Rezepte können Spuren von Tipp- und Denkfehlern enthalten.
                Wenn du welche findest, mail an fettnapf3000 ät posteo punkt de</a>!
                </div>
            """, False)

    def plan_oneoff(self, menu_md):
        moji = randomoji_control(self.root + "/menu?menu=" + urllib.parse.quote(menu_md), "editieren")
        return self.html_body("calculate",
            f"""{moji}
                {self.menu_html(menu_md)}
                <hr>
                <div style="text-align: center;">
                Rezepte können Spuren von Tipp- und Denkfehlern enthalten.
                Wenn du welche findest, mail an fettnapf3000 ät posteo punkt de</a>!
                </div>
            """, False)
