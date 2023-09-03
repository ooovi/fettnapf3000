import os
import sys
import urllib.parse
import parser
import planner
from http.server import HTTPServer, BaseHTTPRequestHandler
#from pypandoc import convert_text
import markdown

DEFAULT_PORT = 8080

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/recipes":
            self.get_recipes()
        elif self.path.startswith("/calculate"):
            self.get_calculate()
        else:
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(bytes("<html><head><title>fettnapf 3000 recipes</title></head>", "utf-8"))
            self.wfile.write(bytes("<body>", "utf-8"))
            self.wfile.write(bytes(self.path + "is no valid path!", "utf-8"))
            self.wfile.write(bytes("</body></html>", "utf-8"))

    def get_recipes(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        recipes = os.listdir("recipes")
        self.wfile.write(bytes("<html><head><title>fettnapf 3000 recipes</title></head>", "utf-8"))
        self.wfile.write(bytes("<body>", "utf-8"))
        [self.wfile.write(bytes(recipe + "<br>", "utf-8")) for recipe in recipes]
        self.wfile.write(bytes("</body></html>", "utf-8"))

    def get_calculate(self):
        self.send_response(200)
        # self.send_header('Content-type', 'application/pdf')
        self.send_header("Content-type", "text/html")
        self.end_headers()
        params = urllib.parse.parse_qs(self.path[self.path.rfind("?") + 1:])
        recipe_name = params.get("recipe").pop()
        quantity = int(params.get("quantity").pop())
        # self.wfile.write(bytes("recipe: " + recipe_name + "<br>", "utf-8"))
        # self.wfile.write(bytes("quantity: " + str(quantity) + "<br>", "utf-8"))
        recipe = parser.parse_recipe("recipes/" + recipe_name)
        menu = {"recipe": [(recipe, quantity)]}
        plan = planner.plan(menu)
        file_path = "/tmp/result.pdf"
        # convert_text(plan, 'pdf', format='md', outputfile=file_path)
        self.wfile.write(bytes("<html><head><title>"
                               + str(quantity)
                               + " " + recipe_name
                               + "</title></head>", "utf-8"))
        self.wfile.write(bytes("<body>", "utf-8"))
        self.wfile.write(bytes(markdown.markdown(plan, extensions=['extra']), "utf-8"))
        self.wfile.write(bytes("</body></html>", "utf-8"))
        # with open(file_path, 'rb') as file:
        #     self.wfile.write(file.read())
        # os.remove(file_path)


os.chdir('.')
if len(sys.argv) == 2:
    port = sys.argv[1]
else:
    port = DEFAULT_PORT
server_object = HTTPServer(server_address=('', int(port)), RequestHandlerClass=MyServer)
server_object.serve_forever()
