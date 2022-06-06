# fettnapf3000

A tool for planning almost-arbitrary-scale cooking activities. Can generate a menu, shopping list and cookbook given the recipes and desired number of servings. Content is inspired by the amazing [fettnapf cookbook](https://food4action.noblogs.org/fettnapf/).

### Requirements
- [python](https://www.python.org/) >= 3.6
- the [pyparsing](https://pypi.org/project/pyparsing/) python package
- the [tinydb](https://pypi.org/project/tinydb/) python package
- [pypandoc](https://pypi.org/project/pypandoc/) for pdf export

### Usage
#### Recipes
Recipes are stored in the `recipes` folder. Ingredients are in german but I have translations if you want them. They are markdown files that look like this:
```
## Super shake
42 portionen

### Zutaten
1 zwiebeln
1 knoblauch
1 ingwer

### Anleitung
blend all ingredients. enjoy.

### Material
blender
```
The instructions and materials sections are each optional. Take care to use the same spellings for ingredients as in the other recipes otherwise you won't get all the benefits. Ingredient quantities are assumed to be given in kilograms.

#### Menus
Create a menu file containing the number of servings you want to prepare per recipe. The file must consist of markdown 3rd-level headings followed by newline-seperated number of servings and recipe filenames (they have to exist in the recipe folder). For example:
```
### Monday
1 supershake

### Tuesday
1 supershake

### Rest of the week
100 coffee
100 pumpkinsnails
```
Check out the `repertoire.txt` file, it has all the recipes!

#### Plan!
Call the program by entering the following command from within the project directory:
```
python src/fettnapf3000 example_menu.txt
```
It will store a pdf file in the same folder as the menu.

Your new PDF file has:
- A nice overview over your menu
- Two copies of the shopping list, sorted by how my favourite wholesale is sorted
- A list of recipes already scaled to the requested number of servings, sorted like in the menu file with pagebreaks where you put the sections.


#### For power users
Only ingredients that are already used in recipes will appear in a sorted fashion in the shopping list. Unknown ingredients will simply appear in the "None" category. If you want to add new ingredients, edit the file `metrodb.py`
