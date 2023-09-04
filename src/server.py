import os
import sys
import urllib.parse
import parser
import planner
from http.server import HTTPServer, BaseHTTPRequestHandler
import markdown2

DEFAULT_ADDR = ''
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
        self.wfile_write(
            "<html>\
            <head>\
            <title>fettnapf 3000 recipes</title>\
            <style>\
            form  { display: table;      }\
            p     { display: table-row;  }\
            label { display: table-cell; }\
            input { display: table-cell; }\
            </style>\
            </head>")
        self.wfile_write("<body>")
        hint = "<strong>Stelle Anzahl Portionen pro Gericht ein und drueck auf Kalkulation!</strong>"  \
        "<br> Speicher danach den Link, um deine Kalkulation zu teilen.<br><br>"
        self.wfile_write(hint)
        self.wfile_write(self.create_recipes_form())
        self.wfile_write("</body></html>")

    def create_recipes_form(self):
        recipes = os.listdir("recipes")
        html_string = " <form action=\"/calculate\" method=\"get\">"
        for recipe in recipes:
            html_string += "<p>\
                <label for=\"" + recipe + "\">" + os.path.splitext(recipe)[0].capitalize().replace("_"," ") + ":&ensp;</label>\
                <input type=\"number\" name=\"" + recipe + "\" size=\"6\"><br>\
                </p>"
        html_string += "<input type=\"submit\" value=\"Kalkulation\"></form>"
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
        
        self.wfile_write("<html>\
            <head>\
            <style>\
            body { \
            	max-width: 1080px; \
            	margin: 10 auto !important; \
            	float: none !important; \
            }\
            h1 {border-top: 2px solid lightgrey; padding-top:50px}\
            table {\
               border-collapse: collapse;\
               margin: 25px 0;\
               min-width: 400px;\
            }\
            table tr:nth-child(even) td { background-color: #f2f2f2;}\
            table td { padding: 10px; }\
            </style>\
            <title>Fettnapf3000 Power Kalkulator!</title></head>")
        self.wfile_write("<body>")
        self.wfile_write(plan_html)
        self.wfile_write("</body></html>")

    def wfile_write(self, string):
        self.wfile.write(bytes(string, "utf-8"))

os.chdir('.')
if len(sys.argv) == 3:
    addr = sys.argv[1]
    port = sys.argv[2]
if len(sys.argv) == 2:
    addr = DEFAULT_ADDR
    port = sys.argv[1]
else:
    addr = DEFAULT_ADDR
    port = DEFAULT_PORT
server_object = HTTPServer(server_address=(addr, int(port)), RequestHandlerClass=MyServer)
server_object.serve_forever()
