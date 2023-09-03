import os
import sys
import urllib.parse
import parser
import planner
from http.server import HTTPServer, BaseHTTPRequestHandler
#from pypandoc import convert_text
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
        button = "Stelle Menge pro Gericht ein und drueck auf Kalkulation!"
        button += "<button onclick=\"window.location.href='calculate?recipe=apfelkrapfen.txt&quantity=1000';\">Kalkulation</button>"
        self.wfile_write(button)
        self.wfile_write(self.test_form())
        self.wfile_write(self.create_recipes_table())
        self.wfile_write("</body></html>")

    def create_recipes_table(self):
        html_string = "<table>"
        html_string += "<tr> <th>Rezept</th> <th>Menge</th> </tr>"
        recipes = os.listdir("recipes")
        for recipe in recipes:
            html_string += "<tr> <td>" + recipe + "</td> <td> <input type=\"number\"> </td> </tr>"
        html_string += "</table>"
        return html_string

    def test_form(self):
        html_string = " <form action=\"/calculate\" method=\"get\">" \
                       "  <label for=\"bollo.txt\">bollo:</label>" \
                       "  <input type=\"text\" id=\"id0\" name=\"bollo.txt\"><br><br>" \
                       "  <label for=\"ful.txt\">ful:</label>" \
                       "  <input type=\"text\" id=\"id1\" name=\"ful.txt\"><br><br>" \
                       "  <input type=\"submit\" value=\"Submit\">" \
                       "</form> "
        return html_string

    def get_calculate(self):
        self.send_response(200)
        # self.send_header('Content-type', 'application/pdf')
        self.send_header("Content-type", CONTENT_TYPE)
        self.end_headers()
        params = urllib.parse.parse_qs(self.path[self.path.rfind("?") + 1:])
        recipe_name = params.get("recipe").pop()
        quantity = int(params.get("quantity").pop())
        recipe = parser.parse_recipe("recipes/" + recipe_name)
        menu = {"recipe": [(recipe, quantity)]}
        
        plan = planner.plan(menu)
        plan_html = markdown2.markdown(plan, extras=['tables','task_list'])
        
        self.wfile_write("<html><head><title>"
                               + str(quantity)
                               + " " + recipe_name
                               + "</title></head>")
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
