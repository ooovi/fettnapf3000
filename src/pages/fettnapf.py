from tinydb import Query
import markdown
import urllib.parse
import pymdownx
import cherrypy
import parser
import planner
from recipe import Recipe
from utils import randomoji, randomoji_control
from i18n import get_i18n, get_languages, category_name_to_id


class FettnapfPage:
    def __init__(self, db, user="team"):
        self.db = db
        self.user = user
        if not user == "team":
            self.root = "/" + user
        else:
            self.root = ""
    def get_translator(self):
        return get_i18n(self.get_language())

    def gettext(self):
        return self.get_translator().gettext

    def get_language(self):
        if 'lang' in cherrypy.request.cookie:
            lang = cherrypy.request.cookie['lang'].value
        else:
            lang = cherrypy.request.headers.get('Accept-Language', 'en').split(',')[0][:2]

        if lang in get_languages():
            return lang
        else:
            return 'en'

    @cherrypy.expose
    def set_lang(self, **kwargs):
        lang = kwargs.get("lang")
        if lang in get_languages():
            cherrypy.response.cookie['lang'] = lang

        referer = cherrypy.request.headers.get('Referer','/')
        if referer:
            raise cherrypy.HTTPRedirect(referer, status=302)
        else:
            raise cherrypy.HTTPRedirect("/", status=302)

    def html_body(self, css, body, add_footer=True):
        _ = self.gettext()
        footer = ""
        language_links = []

        cur_lang = self.get_translator().info()['language']
        if cur_lang != 'de':
            language_links.append('<a href="/set_lang?lang=de">Deutsch</a>')
        if cur_lang != 'en':
            language_links.append('<a href="/set_lang?lang=en">English</a>')
        

        footer = f"""
                    <hr class="no-print">
                    <nav style="text-align:center;" class="no-print">
                    <a href="{self.root}/">{_("Recipe planner")}</a> |
                    <a href="{self.root}/menu/">{_("Menu planner")}</a> |
                    <a href="{self.root}/repertoire/">{_("Manage repertoire")}</a>
                    <br>
                    {" | ".join(language_links)}
                </nav>
                    <footer class="no-print" style="margin-top: 3em; text-align: center;">
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
                     <link href="/static/css/main.css" rel="stylesheet">
                     <link href="/static/css/{css}.css" rel="stylesheet">
                     <link href="/static/pwa_manifest.json" rel="manifest">
                     <link href="/static/favicon.ico" rel="icon">
                     <title>{_("page_title")}</title>
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
        _ = self.gettext()
        html_str = """<dl style="list-style-type:none;">"""
        for (cat, recipes) in sorted(self.recipes_cat().items()):
            recipes.sort()
            recipe_links = []
            for recipe in recipes:
                if edit:
                    link = f"repertoire/edit_recipe/?name={urllib.parse.quote(recipe)}"
                else:
                    link = f"calculate?{urllib.parse.quote(recipe)}=10"
                recipe_links.append(f"""<a href="{self.root}/{link}">{recipe.capitalize().replace("_"," ")}</a>""")
            html_str += f"<dt style=\"font-size:1.2em;padding-top:0.5em\"><strong>{_(category_name_to_id(cat))}</strong></dt>"
            html_str += "".join("<dd>" + recipe + "</dd>" for recipe in recipe_links)
        return html_str + "</dl>"

    def plan_menu(self, menu_md):
        _ = self.gettext()
        try:
            menu_list = parser.parse_menu(menu_md)
        except parser.ParseError as e:
            return self.error_page(f"""<strong>{_("Your menu is not in the correct format!")}</strong><br>
                        {_("Go back and look at it again. The mistake:")}<br>
                        <div>{e}</div>
                     """)
        menu = {}
        for (category, recipe_name, n_servings) in menu_list:
             recipe_entries = self.db.search(Query().name == recipe_name)
             if recipe_entries:
                 recipe = Recipe.from_document(recipe_entries[0])
             else:
                 return self.error_page(f"""<strong>{_("The recipe \"%s\" is not on the list!") % recipe_name.capitalize().replace("_"," ")}</strong><br>
                        {_("Go back and look at it again.")}
                     """)
             if category in menu:
                 menu[category].append((recipe, n_servings))
             else:
                 menu[category] = [(recipe, n_servings)]

        plan = planner.plan(menu, self.get_language())
    
        extension_configs = { 'pymdownx.tasklist': {'clickable_checkbox': 'True' } }
        plan_html = markdown.markdown(plan,
            extensions=['tables','pymdownx.tasklist'],
            extension_configs=extension_configs)

        moji = randomoji_control(self.root + "/menu/?menu=" + urllib.parse.quote(menu_md), _("edit"))

        return self.html_body("calculate",
            f"""{moji}
                {plan_html}
                <hr>
                <div style="text-align: center;">
                 {_("Recipes may contain traces of typing and mental errors.")}
                 {_("If you find any, mail to fettnapf3000 ät posteo dot de")}</a>!
                </div>
            """, False)
