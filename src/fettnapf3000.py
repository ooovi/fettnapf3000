import sys
from parser import parse_menu, parse_recipe, ParseError
from planner import plan
from pypandoc import convert_text

def main():
    menu_file = sys.argv[1]

    try:
       menu_list = parse_menu(menu_file)

       # make a menu dict, mapping categories to lists of recipes and n_servings
       menu = {}
       for (category, recipe_name, n_servings) in menu_list:
            recipe_file = sys.path[0] + "/../recipes/" + recipe_name + ".txt"
            recipe = parse_recipe(recipe_file)
            if category in menu:
                menu[category].append((recipe, n_servings))
            else:
                menu[category] = [(recipe, n_servings)]

       # make a plan!
       plan_markdown = plan(menu)

       # convert to pdf using pypandoc and write it to file
       convert_text(plan_markdown, 'pdf', format='md', outputfile=menu_file+".pdf")

           
    except IOError as e:
        print(f"Error handling file {recipe_file}.\n {e}")
        sys.exit(1)
    except ParseError as e:
        print(f"Error parsing.\n {e}")
        sys.exit(1)


main()
