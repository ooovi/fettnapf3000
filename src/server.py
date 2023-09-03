import os
import sys
import urllib.parse
import parser
import planner
from http.server import HTTPServer, BaseHTTPRequestHandler
import markdown2

DEFAULT_PORT = 8080
CONTENT_TYPE = "text/html; charset=utf-8"


class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/recipes":
            self.get_recipes()
        elif self.path.startswith("/calculate"):
            self.get_calculate()
        else:
            self.send_response(200)
            self.send_header("Content-type", CONTENT_TYPE)
            self.end_headers()
            self.wfile_write("<html><head><title>fettnapf 3000 recipes</title></head>")
            self.wfile_write("<body>")
            self.wfile_write(self.path + "is no valid path!")
            self.wfile_write("</body></html>")

    def get_recipes(self):
        self.send_response(200)
        self.send_header("Content-type", CONTENT_TYPE)
        self.end_headers()
        self.wfile_write("<html><head><title>fettnapf 3000 recipes</title></head>")
        self.wfile_write("<body>")
        hint = "<strong>Stelle Menge pro Gericht ein und drueck auf Kalkulation!</strong>"  \
        "<br> Speicher danach den Link, um deine Kalkulation zu teilen.<br><br>"
        self.wfile_write(hint)
        self.wfile_write(self.create_recipes_form())
        self.wfile_write("</body></html>")

    def create_recipes_form(self):
        recipes = os.listdir("recipes")
        html_string = " <form action=\"/calculate\" method=\"get\">"
        for recipe in recipes:
            html_string += "<label for=\"" + recipe + "\">" + recipe + ":</label><input type=\"number\" name=\"" + recipe + "\"><br>"
        html_string += "<input type=\"submit\" value=\"Kalkulation\"></form> "
        return html_string

    def get_calculate(self):
        self.send_response(200)
        self.send_header("Content-type", CONTENT_TYPE)
        self.end_headers()
        params = urllib.parse.parse_qs(self.path[self.path.rfind("?") + 1:])

        menu = {}
        for recipe_name in params:
            recipe = parser.parse_recipe("recipes/" + recipe_name)
            n_servings = int(params.get(recipe_name).pop())
            if "Rezepte" in menu:
                 menu["Rezepte"].append((recipe, n_servings))
            else:
                 menu["Rezepte"] = [(recipe, n_servings)]
            
        plan = planner.plan(menu)
        plan_html = markdown2.markdown(plan, extras=['tables','task_list'])
        
        self.wfile_write("<html><head><title>Fettnapf3000 power kalkulator!</title></head>")
        self.wfile_write("<body>")
        self.wfile_write(plan_html)
        self.wfile_write("</body></html>")

    def wfile_write(self, string):
        self.wfile.write(bytes(string, "utf-8"))

os.chdir('.')
if len(sys.argv) == 2:
    port = sys.argv[1]
else:
    port = DEFAULT_PORT
server_object = HTTPServer(server_address=('', int(port)), RequestHandlerClass=MyServer)
server_object.serve_forever()
