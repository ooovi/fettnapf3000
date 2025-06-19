import cherrypy
import urllib.parse
from pages.fettnapf import FettnapfPage
from utils import randomoji_link

class RecipePage(FettnapfPage):
    
    @cherrypy.expose
    def index(self):
        _ = self.gettext()
        return self.html_body("recipes",
        f"""{randomoji_link("menu")}
            <strong>{_("Set the number of portions per dish and press calculate!")}</strong>
            <p>{_("rezeptplanner_description")}</p>
            {self.create_recipes_form()}
        """)

    def create_recipes_form(self):
        _ = self.gettext()
        html_string = f" <form action=\"{self.root}/request\" method=\"get\">"
        for (cat, recipes) in self.recipes_cat().items():
            html_string += f"<h2>{_(cat.capitalize())}</h2>"
            for recipe in recipes:
                html_string += f"""<p>
                <label for="{recipe}">
                 {recipe.capitalize()}:&ensp;
                </label>
                <input type="number" name="{recipe}" id="{recipe}"><br>
                </p>"""
        html_string += f"""<p><input type="submit" value="{_("Calculation")}"></p></form>"""
        return html_string

    @cherrypy.expose
    def menu(self, **kwargs):
        _ = self.gettext()
        menu = ""
        if kwargs:
            menu = kwargs.get("menu")

        return self.html_body("menu",
            f"""{randomoji_link(self.root + "/")}
                <strong>{_("Specify a menu in this format:")}</strong>
                <div><pre>
### Montag
1 Super shake

### Dienstag
1 Super shake

### Rest der Woche
100 Kaffe
100 Kürbisschnecken mit orangenbutter
                </pre></div>
                {_("menu_instructions")}
                <form action="{self.root}/calculate_menu" method="get" >
                 <textarea name="menu">{menu}</textarea><br>
                 <p><input type="submit" value="{_("Calculation")}"></p>
                </form>
               <h1>{_("Recipes")}</h1>
               {self.recipe_list()}
            """)
    
    @cherrypy.expose
    def calculate_menu(self, **kwargs):
        return self.plan_menu(kwargs.get("menu"))

    @cherrypy.expose
    def request(self, **kwargs):
        # clean empty form entries from url
        clean_request = { (r,n) for (r,n) in kwargs.items() if n }
        raise cherrypy.HTTPRedirect(
            f"{self.root}/calculate/?" + '&'.join(f"{urllib.parse.quote(r)}={n}" for (r,n) in clean_request)
        )

    @cherrypy.expose
    def calculate(self, **kwargs):
        _ = self.gettext()
        if not kwargs:
            raise cherrypy.HTTPRedirect(f"/{self.root}")

        return self.plan_menu(f"### {_("Recipes")}\n" + "\n".join(f"{n} {recipe_name}" for (recipe_name, n) in kwargs.items()))
