import sys
import os, os.path
import cherrypy
import markdown
import pymdownx
import planner
import parser
from random import choice
import urllib.parse

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
                   "&#127789;"])

def favicon():
   return """<link rel="icon"
                  href="data:image/svg+xml,
                        <svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22>
                         <text y=%22.9em%22 font-size=%2290%22>&#127814;</text>
                        </svg>"
              >"""

def viewport():
    return """<meta name="viewport" content="width=device-width, initial-scale=1.0">"""


class RecipePage:
    @cherrypy.expose
    def index(self):
        return f"""<html>
              {viewport()}
              <head>
               <link href="./static/css/recipes.css" rel="stylesheet">
               {favicon()}
               <title>fettnapf3000 Power Kalkulator!</title>
             </head>
             <body>
              <center><p style="font-size:70px;">
               {randomoji()}
              </p></center>
              <strong>Stelle Anzahl Portionen pro Gericht ein und drück auf Kalkulation!</strong>
              <br> Speicher danach den Link, um deine Kalkulation zu teilen.<br><br>
              {self.create_recipes_form()}
            </body>
            <center>
            <footer>
              <p>made with &#127814; by team geil</p>
              <p>contribute on <a href="https://github.com/ooovi/fettnapf3000">github</a></p>
            </footer>
            </center>
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
                <input type="number" name="{recipe}" size="6"><br>
                </p>"""
        html_string += "<input type=\"submit\" value=\"Kalkulation\"></form>"
        return html_string

class RequestPage:
    @cherrypy.expose
    def index(self, **kwargs):
        # clean empty form entries from url
        clean_request = { (r,n) for (r,n) in kwargs.items() if n }
        if len(clean_request) != len(kwargs):
            raise cherrypy.HTTPRedirect(
                "/calculate/?" + '&'.join(f"{urllib.parse.quote(r)}={n}" for (r,n) in clean_request)
            )

class CalculatePage:
    @cherrypy.expose
    def index(self, **kwargs):
        menu = {}
        for (recipe_name, n) in kwargs.items():
            if n:
                recipe = parser.parse_recipe("../recipes/" + recipe_name)
                n_servings = int(n)
                if "Rezepte" in menu:
                     menu["Rezepte"].append((recipe, n_servings))
                else:
                     menu["Rezepte"] = [(recipe, n_servings)]
            
        plan = planner.plan(menu)

        extension_configs = { 'pymdownx.tasklist': {'clickable_checkbox': 'True' } }
        plan_html = markdown.markdown(plan,
            extensions=['tables','pymdownx.tasklist'],
            extension_configs=extension_configs)

        return f"""<html>
            {viewport()}
            <head>
             <link href="../static/css/calculate.css" rel="stylesheet">
             {favicon()}
             <title>fettnapf3000 Power Kalkulator!</title>
            </head>
             <body>
              <center><p style="font-size:70px;">
               <a href="/">
                {randomoji()}
               </a>
              </p></center>
              {plan_html}
             </body>
           </html>"""

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
    root.calculate = CalculatePage()
    cherrypy.quickstart(root, config = conf)