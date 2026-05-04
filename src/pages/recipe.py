import cherrypy
import urllib.parse
from pages.fettnapf import FettnapfPage
from utils import randomoji_link

class RecipePage(FettnapfPage):
    
    @cherrypy.expose
    def index(self):
        return self.html_body("recipes",
        f"""{randomoji_link("menu")}
            <strong>Stelle Anzahl Portionen pro Gericht ein und drück auf Kalkulation!</strong>
            <br> Speicher danach den Link, um deine Kalkulation zu teilen, oder drucke die Seite aus.
            <br> Falls du viele verschiedene Gerichte planst könnte dich unser <a href="./menu">Menü-Planer</a> interessieren!
            <br> Falls du eine Koche organisieren willst, lad dir den <a href="https://food4action.noblogs.org/fettnapf/">Fettnapf</a> runter, das ultimative SoKü-Handbuch unserer Herzen.<br>
            {self.create_recipes_form()}
        """)

    def create_recipes_form(self):
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

    @cherrypy.expose
    def menu(self, **kwargs):
        menu = ""
        if kwargs:
            menu = kwargs.get("menu")

        return self.html_body("menu",
            f"""{randomoji_link(self.root + "/")}
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
                Drück auf Kalkulation. Speicher danach den Link, um deine Kalkulation zu teilen, oder drucke die Seite aus.
                <form action="{self.root}/calculate_menu" method="get" >
                 <textarea name="menu">{menu}</textarea><br>
                 <p><input type="submit" value="Kalkulation"></p>
                </form>
               <h1>Rezepte</h1>
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
        if not kwargs:
            raise cherrypy.HTTPRedirect(f"/{self.root}")

        return self.plan_menu("### Rezepte\n" + "\n".join(f"{n} {recipe_name}" for (recipe_name, n) in kwargs.items()))

