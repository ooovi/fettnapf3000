from pyparsing import (
    ParseException,
    OneOrMore,
    ZeroOrMore,
    CaselessKeyword,
    Suppress,
    White,
    Word,
    Combine,
    Group,
    Optional,
    LineEnd,
    Dict,
    Each,
    CharsNotIn,
    tokenMap,
    nums,
)
from collections import Counter
from planner import Recipe


## parser for recipe files
#

word = OneOrMore(CharsNotIn('\n'))
word.setParseAction(tokenMap(lambda t : t.lower().strip()))

weight = Combine(Word(nums) + Optional('.' + Word(nums)))
weight.setParseAction(tokenMap(float))

def section(header, body):
    return maybebreaks + Suppress(CaselessKeyword("### " + header)) + linebreaks + body + maybebreaks

linebreak = Suppress(LineEnd())
linebreaks = OneOrMore(linebreak)
maybebreaks = ZeroOrMore(linebreak)

title = Suppress("## ") + word + linebreaks

servings = weight + Suppress("Portionen") + linebreaks

ingredient = weight + Suppress(ZeroOrMore(' ')) + word + linebreak
ingredient.setParseAction(lambda l : tuple(reversed(l))) # reverse so it fits the Counter constructor

ingredients = section("Zutaten", OneOrMore(ingredient))

instructions = section("Anleitung", OneOrMore(CharsNotIn('\n')))

materials = section("Material", OneOrMore(word + linebreak))

recipe_parser = title("name")\
              + servings("servings")\
              + (ingredients("ingredients")\
              & Optional(instructions)("instructions")\
              & Optional(materials)("materials"))

## build a Recipe object from file
#

class ParseError(Exception):
    pass

def build_recipe(recipe_string):
    try:
        parsed_recipe = recipe_parser.parseString(recipe_string)
    except ParseException as err:
        raise ParseError(f"Recipe {recipe_string} not formatted correctly, got error\n {err}")
        
    name = parsed_recipe.name[0]
    servings = parsed_recipe.servings[0]
    if servings == 0:
        raise ParseError(f"Error parsing recipe {name}: zero number of servings")
    else:
        recipe_counter = Counter({ingredient: amount / servings
                                              for (ingredient, amount) in parsed_recipe["ingredients"]})

        instr = parsed_recipe["instructions"][0] if "instructions" in parsed_recipe else ""
        mat = set(parsed_recipe["materials"]) if "materials" in parsed_recipe else set()

        return Recipe(name, recipe_counter, instr, mat)


def parse_recipe(path):
    with open(path, 'r') as readfile:
        recipe_string = readfile.read()
        return build_recipe(recipe_string)


## parse a menu file
#

category = Group(Suppress("### ") + word("name") + OneOrMore(ingredient + Optional(linebreaks))("recipes"))
menu_parser = OneOrMore(category)

# returns a list of tuples (category, recipe filename, number of servings)
def parse_menu(path) -> list[tuple[str, str, float]]:
    with open(path, 'r') as file:
        menu_string = file.read()
        try:
            parsed_menu = menu_parser.parseString(menu_string)
        except ParseException as err:
            raise ParseError(f"Menu not formatted correctly, got error {err}")
        menu = []
        for cat in parsed_menu:
            cat_name = cat.name[0]
            for (recipe_name, servings) in cat.recipes:
                menu.append((cat_name, recipe_name, servings))
        return menu

