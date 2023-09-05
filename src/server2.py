import os, os.path
import cherrypy
import markdown
import pymdownx
import planner
import parser

class RecipePage:
    @cherrypy.expose
    def index(self):
        return f"""<html>
          <head>
            <link href="./static/css/recipes.css" rel="stylesheet">
            <link rel="icon"
                  href="data:image/svg+xml,
                        <svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22>
                         <text y=%22.9em%22 font-size=%2290%22>&#127814;</text>
                        </svg>"
            >
            <title>fettnapf3000 Power Kalkulator!</title>
          </head>
          <body>
           <center><p style="font-size:70px;">
            &#127814;
           </p></center>
           <strong>Stelle Anzahl Portionen pro Gericht ein und drück auf Kalkulation!</strong>
           <br> Speicher danach den Link, um deine Kalkulation zu teilen.<br><br>
           {self.create_recipes_form()}
         </body>
        </html>"""

    def create_recipes_form(self):
        recipes = os.listdir("../recipes")
        recipes.sort()
        html_string = " <form action=\"/calculate\" method=\"get\">"
        for recipe in recipes:
            html_string += f"""<p>
                <label for="{recipe}">
                 {os.path.splitext(recipe)[0].capitalize().replace("_"," ")}:&ensp;
                </label>
                <input type="number" name="{recipe}" size="6"><br>
                </p>"""
        html_string += "<input type=\"submit\" value=\"Kalkulation\"></form>"
        return html_string

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
             <head>
              <link href="../static/css/calculate.css" rel="stylesheet">
              <link rel="icon"
                    href="data:image/svg+xml,
                          <svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22>
                           <text y=%22.9em%22 font-size=%2290%22>&#127814;</text>
                          </svg>"
              >
              <title>fettnapf3000 Power Kalkulator!</title>
             </head>
           <center><p style="font-size:70px;">
            <a href="/">&#127814;</a>
           </p></center>
             <body>
              {plan_html}
             </body>
            </html>"""



if __name__ == '__main__':
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
    cherrypy.server.socket_port = 8082
    root = RecipePage()
    root.calculate = CalculatePage()
    cherrypy.quickstart(root, config = conf)