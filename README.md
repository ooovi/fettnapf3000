# fettnapf3000 🍆

A tool for planning almost-arbitrary-scale cooking activities. Can generate a menu, shopping list and cookbook given the recipes and desired number of servings. Content is inspired by the amazing [fettnapf cookbook](https://food4action.noblogs.org/fettnapf/).

### Requirements
- [python](https://www.python.org/) >= 3.9
- the [pyparsing](https://pypi.org/project/pyparsing/) python package
- the [tinydb](https://pypi.org/project/tinydb/) python package
- the [CherryPy](https://pypi.org/project/CherryPy/) python package for the web interface
- [pypandoc](https://pypi.org/project/pypandoc/) for pdf export

## Usage
### Web interface (recommended)

We host an instance with our recipes [here](https://teamgeil.uber.space).

To start a local server serving the fettnapf at port 8000, navigate to the `src` directory and run
```python
python server.py 8000
```
You may now use the web interface by navigating to [`http://localhost:8000`](http://localhost:8000) in your browser.

To make the server listen on a network interface different from localhost (e.g. `0.0.0.0`), run
```python
python server.py 0.0.0.0 8000
```

### Command line
#### Menu file
Create a menu file containing the number of servings you want to prepare per recipe. The file must consist of markdown 3rd-level headings followed by newline-seperated number of servings and recipe names (they have to exist in the recipe database). For example:
```
### Monday
1 supershake

### Tuesday
1 supershake

### Rest of the week
100 coffee
100 pumpkinsnails
```

#### Recipes
Our recipe databases are kept in a [separeate repository](https://github.com/ooovi/fettnapf3000recipes). Clone that and place it next to the directory of this repo. If you want to use your own database, adjust the path in line 19 of `server.py`. 

#### Plan!
Call the program by entering the following command from within the project directory:
```
python src/fettnapf3000 example_menu.txt
```
It will store a pdf file in the same folder as the menu if you have `pypandoc` installed. Otherwise, you'll get a plain text markdown file.

Your new file has:
- A nice overview over your menu
- Two copies of the shopping list, sorted by how my favourite wholesale is sorted
- A list of recipes already scaled to the requested number of servings, sorted like in the menu file with pagebreaks where you put the sections.


#### For power users
Only ingredients that are already used in recipes will appear in a sorted fashion in the shopping list. Unknown ingredients will simply appear in the "None" category. If you want to add new ingredients, edit the file `metrodb.py`
