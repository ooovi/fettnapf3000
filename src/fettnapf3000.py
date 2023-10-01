import sys
import importlib
from parser import parse_menu_file, parse_recipe, ParseError
from planner import plan
from recipe import Recipe
from tinydb import TinyDB, Query

def main():
    menu_file = sys.argv[1]
    recipes_file = sys.argv[2]

    try:
       menu_list = parse_menu_file(menu_file)

       # make a menu dict, mapping categories to lists of recipes and n_servings
       recipe_db = TinyDB(recipes_file)
       menu = {}
       for (category, recipe_name, n_servings) in menu_list:
           recipe_entries = recipe_db.search(Query().name == recipe_name)
           if recipe_entries:
               recipe = Recipe.from_document(recipe_entries[0])
           else:
               print(f"Recipe {recipe_name.capitalize()} not found.")
               sys.exit(1)
           if category in menu:
               menu[category].append((recipe, n_servings))
           else:
               menu[category] = [(recipe, n_servings)]

       # make a plan!
       plan_markdown = plan(menu)

       if importlib.util.find_spec('pypandoc'):
           # convert to pdf using pypandoc and write it to file
           from pypandoc import convert_text
           convert_text(
                plan_markdown,
                'pdf',
                format='md',
                outputfile=menu_file+".pdf",
                extra_args=['-V', 'geometry:margin=2.5cm', '-V', 'fontsize=12pt']
            )
       else:
           print("PDF export requires pypandoc to be installed. Saving markdown file instead.")
           with open(menu_file + ".md", "w") as file:
               file.write(plan_markdown)
           
    except IOError as e:
        print(f"Error handling file {recipe_file}.\n {e}")
        sys.exit(1)
    except ParseError as e:
        print(f"Error parsing.\n {e}")
        sys.exit(1)


main()
