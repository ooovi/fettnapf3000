import cherrypy
from tinydb import Query
import urllib.parse
from pages.fettnapf import FettnapfPage, urldb
from utils import randomoji, randomoji_link

class RecipePage(FettnapfPage):

    # the recipe list page with number input
    @cherrypy.expose
    def index(self):
        def recipes_form():
            html_string = f" <form action=\"{self.root}/request\" method=\"get\">"
            for (cat, recipes) in self.recipes_cat().items():
                html_string += f"<h2>{cat.capitalize()}</h2>"
                for recipe in recipes:
                    html_string += f"""<p>
                    <label for="{recipe}">
                     {recipe.capitalize()}:&ensp;
                    </label>
                    <input type="number" name="{recipe}" id="{recipe}"><br>
                    </p>"""
            html_string += """<p><input type="submit" value="Kalkulation"></p></form>"""
            return html_string
        return self.html_body("recipes",
        f"""{randomoji_link("menu")}
            <strong>Stelle Anzahl Portionen pro Gericht ein und drück auf Kalkulation!</strong>
            <br> Speicher danach den Link, um deine Kalkulation zu teilen, oder drucke die Seite aus.
            <br> Falls du viele verschiedene Gerichte planst könnte dich unser <a href="./menu">Menü-Planer</a> interessieren!
            <br> Falls du eine Koche organisieren willst, lad dir den <a href="https://food4action.noblogs.org/fettnapf/">Fettnapf</a> runter, das ultimative SoKü-Handbuch unserer Herzen.<br>
            {recipes_form()}
        """)

    @cherrypy.expose
    def request(self, **kwargs):
        # clean empty form entries from url
        clean_request = { (r,n) for (r,n) in kwargs.items() if n }
        raise cherrypy.HTTPRedirect(
            f"{self.root}/calculate?" + '&'.join(f"{urllib.parse.quote(r)}={n}" for (r,n) in clean_request)
        )

    @cherrypy.expose
    def calculate(self, **kwargs):
        if not kwargs:
            raise cherrypy.HTTPRedirect(f"/{self.root}")

        return self.plan_menu("### Rezepte\n" + "\n".join(f"{n} {recipe_name}" for (recipe_name, n) in kwargs.items()))


    # the menu planning page
    @cherrypy.expose
    def menu(self, **kwargs):
        if kwargs.get("id"): # if id was given, we're editing an existing menu
            id = kwargs.get("id")
            id_field = f"""<input type="text" name="id" id="id" value="{id}" required><br><br>"""
            menu = urldb.search(Query().id == id)[0].get("menu_md")
            moji = randomoji_link("")
            button = f"""<p><input type="submit" value="Kalkulation editieren"></p>"""
        else:
            id_field = f"""<input type="text" name="id" id="id" required><br><br>"""
            if kwargs.get("menu"): # if no id, but a menu was given, we're editing something from the recipe list page
                menu = kwargs.get("menu")
                moji = randomoji_link("")
                button = f"""<p><input type="submit" value="Kalkulation speichern"></p>"""
            else: # if nothing was given, it's the standard page
                menu = ""
                moji = randomoji_link(self.root + "/")
                button = f"""<p><input type="submit" value="Kalkulation"></p>"""

        return self.html_body("menu",
            f"""{moji}
                <strong>Gib ein Menü in diesem Format an:</strong>
                <div><pre>
### Montag
1 Super shake

### Dienstag
1 Super shake

### Rest der Woche
100 Kaffe
100 Kürbisschnecken mit orangenbutter
                </pre></div>
                Die Namen der Gerichte müssen genau der Liste unten entsprechen!<br>
            Drück auf Kalkulation. Speicher danach den Link, um deine Kalkulation zu teilen, oder drucke die Seite aus.<br><br>
                <form action="{self.root}/request_menu" method="post">
                 <label for="id">Name für die Kalkulation:</label><br>
                 {id_field}
                 <label for="menu">Menü:</label>
                 <textarea name="menu">{menu}</textarea><br>
                 {button}
                </form>
               <h1>Rezepte</h1>
               {self.recipe_list()}
            """)

    @cherrypy.expose
    def request_menu(self, **kwargs):
        id = kwargs.get("id")
        # make new plan, store in db
        self.plan_menu(kwargs.get("menu"), id)
        raise cherrypy.HTTPRedirect(
            f"{self.root}/plan?id=" + urllib.parse.quote(id)
        )

    # for backwards compat
    @cherrypy.expose
    def calculate_menu(self, **kwargs):
        return self.plan_menu(kwargs.get("menu"))

    @cherrypy.expose
    def plan(self, **kwargs):
        # retrieve plan from database
        return urldb.search(Query().id == kwargs.get("id"))[0].get("html")
