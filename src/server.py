import sys
import os, os.path
import cherrypy
import markdown
import pymdownx
import planner
import parser
from random import choice
import urllib.parse

footer = """<footer style="margin-top: 5em; text-align: center;">
              <p>made with &#127814; by team geil</p>
              <p>contribute on <a href="https://github.com/ooovi/fettnapf3000">github</a></p>
            </footer>"""

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

def favicon():
   return """<link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>&#127814;</text></svg>">"""

def viewport():
    return """<meta name="viewport" content="width=device-width, initial-scale=1.0">"""


def plan_menu(menu):
    plan = planner.plan(menu)

    extension_configs = { 'pymdownx.tasklist': {'clickable_checkbox': 'True' } }
    plan_html = markdown.markdown(plan,
        extensions=['tables','pymdownx.tasklist'],
        extension_configs=extension_configs)

    return f"""
    <!DOCTYPE html>
    <html lang="de">
        <head>
         <meta charset="UTF-8">
         {viewport()}
         <link href="../static/css/calculate.css" rel="stylesheet">
         {favicon()}
         <title>fettnapf3000 Power Kalkulator!</title>
        </head>
        <body>
         {randomoji_link("/")}
         {plan_html}
         <hr>
         <footer style="margin-top: 5em; text-align: center;">
           <p>Rezepte können Spuren von Tipp- und Denkfehlern enthalten.</p>
           <p>Wenn du welche findest, <a href="https://github.com/ooovi/fettnapf3000">sag Bescheid</a>!</p>
         </footer>
        </body>
       </html>"""

class RecipePage:
    @cherrypy.expose
    def index(self):
        return f"""
        <!DOCTYPE html>
        <html lang="de">
              <head>
               <meta charset="UTF-8">
               {viewport()}
               <link href="./static/css/recipes.css" rel="stylesheet">
               {favicon()}
               <title>fettnapf3000 Power Kalkulator!</title>
             </head>
             <body>
              {randomoji_link("/menu")}
              <strong>Stelle Anzahl Portionen pro Gericht ein und drück auf Kalkulation!</strong>
              <br> Speicher danach den Link, um deine Kalkulation zu teilen.
              <br> Falls du viele verschiedene Gerichte planst könnte dich unser <a href="./menu">Menü-Planer</a> interessieren!<br><br>
              {self.create_recipes_form()}
              {footer}
            </body>
            </html>"""

    def create_recipes_form(self):
        recipes = os.listdir("../recipes")
        recipes.sort()
        html_string = " <form action=\"/request\" method=\"get\">"
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
    @cherrypy.expose
    def index(self):
        recipes = os.listdir("../recipes")
        recipes.sort()
        recipe_list = "<br>".join(os.path.splitext(recipe)[0].capitalize() for recipe in recipes)

        return f"""
        <!DOCTYPE html>
        <html lang="de">
            <head>
             <meta charset="UTF-8">
             {viewport()}
             <link href="../static/css/menu.css" rel="stylesheet">
             {favicon()}
             <title>fettnapf3000 Power Kalkulator!</title>
            </head>
             <body>
              {randomoji_link("/")}
              <strong>Gib ein Menü in diesem Format an:</strong>
              <div><pre>
### Montag
1 Supershake

### Dienstag
1 Supershake

### Rest der Woche
100 Kaffe
100 Pumpkinsnails
              </pre></div>
              Die Namen der Gerichte müssen genau der Liste unten entsprechen!<br>
              Drück auf Kalkulation. Speicher danach den Link, um deine Kalkulation zu teilen.
              <form action="/calculate_menu" method="get" >
               <textarea name="menu"></textarea><br>
               <p><input type="submit" value="Kalkulation"></p>
              </form>
             <h1>Rezepte</h1>
             {recipe_list}
             {footer}
             </body>
           </html>"""

class ErrorMenuPage:
    @cherrypy.expose
    def index(self, **kwargs):
        if "format" in kwargs:
            error = f"""<strong>Dein Menü ist nicht im richtigen Format!</strong><br>
                        Geh zurück und schau es dir nochmal an. Der Fehler:<br>
                        <div>{kwargs.get("format")}</div>
                     """
        if "recipe" in kwargs:
            error = f"""<strong>Das Rezept {kwargs.get("recipe")} steht nicht in der Liste!</strong><br>
                        Geh zurück und schau es dir nochmal an.
                     """

        return f"""
        <!DOCTYPE html>
        <html lang="de">
            <head>
             <meta charset="UTF-8">
             {viewport()}
             <link href="../../static/css/menu.css" rel="stylesheet">
             {favicon()}
             <title>fettnapf3000 Power Kalkulator!</title>
            </head>
             <body>
              <p style="font-size:7em; text-align:center;">
               <a href="#" onclick="history.back()" style="text-decoration: none">
               {randomoji()}
               </a></p>
               {error}
             </body>
            </html>"""

class CalculateMenuPage:
    @cherrypy.expose
    def index(self, **kwargs):
        menu_md = kwargs.get("menu")
        try:
            menu_list = parser.parse_menu(menu_md)
        except parser.ParseError as e:
            raise cherrypy.HTTPRedirect(f"/menu/error/?{urllib.parse.urlencode({'format':e})}")
        menu = {}
        for (category, recipe_name, n_servings) in menu_list:
             recipe_file = sys.path[0] + "/../recipes/" + recipe_name + ".txt"
             try:
                 recipe = parser.parse_recipe(recipe_file)
             except IOError as e:
                 raise cherrypy.HTTPRedirect(f"/menu/error/?recipe={recipe_name.capitalize()}")
             if category in menu:
                 menu[category].append((recipe, n_servings))
             else:
                 menu[category] = [(recipe, n_servings)]
        return plan_menu(menu)



class RequestPage:
    @cherrypy.expose
    def index(self, **kwargs):
        # clean empty form entries from url
        clean_request = { (r,n) for (r,n) in kwargs.items() if n }
        raise cherrypy.HTTPRedirect(
            "/calculate/?" + '&'.join(f"{urllib.parse.quote(r)}={n}" for (r,n) in clean_request)
        )

class CalculatePage:
    @cherrypy.expose
    def index(self, **kwargs):
        if not kwargs:
            raise cherrypy.HTTPRedirect("/")

        menu = {}
        for (recipe_name, n) in kwargs.items():
            if n:
                recipe = parser.parse_recipe("../recipes/" + recipe_name)
                n_servings = int(n)
                if "Rezepte" in menu:
                     menu["Rezepte"].append((recipe, n_servings))
                else:
                     menu["Rezepte"] = [(recipe, n_servings)]

        return plan_menu(menu)

if __name__ == '__main__':
    if len(sys.argv) == 3:
        cherrypy.config.update({'server.socket_host': sys.argv[1],
                                'server.socket_port': int(sys.argv[2]),
                               })
    if len(sys.argv) == 2:
        cherrypy.config.update({'server.socket_port': int(sys.argv[1])})
    conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd())
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './public'
        }
    }
    root = RecipePage()
    root.request = RequestPage()
    root.menu = MenuPage()
    root.menu.error = ErrorMenuPage()
    root.calculate_menu = CalculateMenuPage()
    root.calculate = CalculatePage()
    cherrypy.quickstart(root, config = conf)