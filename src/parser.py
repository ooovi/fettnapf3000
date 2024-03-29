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
    MatchFirst
)
from collections import Counter
from recipe import Recipe, recipe_dict
from tinydb import TinyDB
import os, os.path



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
category = Suppress("Kategorie: ") + word + linebreaks

ingredient = weight + Suppress(ZeroOrMore(' ')) + word + linebreak
ingredient.setParseAction(lambda l : tuple(reversed(l))) # reverse so it fits the Counter constructor

ingredient_subsection = Suppress("#### ") + word + linebreaks + OneOrMore(ingredient) + maybebreaks
ingredient_subsection.setParseAction(lambda l : (l[0], l[1:]))

ingredients_notitle = OneOrMore(ingredient) + maybebreaks
ingredients_notitle.setParseAction(lambda l : ("", l))

ingredients = section("Zutaten", MatchFirst([ingredients_notitle, OneOrMore(ingredient_subsection)]))


instructions = section("Anleitung", OneOrMore(CharsNotIn('\n') + linebreak))
instructions.setParseAction(lambda l: '\n'.join(l))

materials = section("Material", OneOrMore(word + linebreak))

recipe_parser = title("name")\
              + servings("servings")\
              + category("category")\
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
        raise ParseError(f"Recipe {recipe_string} not formatted correctly: {err}")
        
    name = parsed_recipe.name[0]
    servings = parsed_recipe.servings[0]
    category = parsed_recipe.category[0]
    if servings == 0:
        raise ParseError(f"Error parsing recipe {name}: zero number of servings")
    else:
        counters = []
        for (subsection, ingredients) in parsed_recipe["ingredients"]:
            counters.append((subsection, Counter({ingredient: amount
                                              for (ingredient, amount) in ingredients})))

        instr = parsed_recipe["instructions"][0] if "instructions" in parsed_recipe else ""
        mat = set(parsed_recipe["materials"]) if "materials" in parsed_recipe else set()

        return Recipe(name, servings, counters, instr, mat, category)


def parse_recipe(path):
    with open(path, 'r') as readfile:
        recipe_string = readfile.read()
        return build_recipe(recipe_string)

## parse a menu file
#

category = Group(Suppress("### ") + word("name") + OneOrMore(ingredient + Optional(linebreaks))("recipes"))
menu_parser = OneOrMore(category)

# returns a list of tuples (category, recipe filename, number of servings)
def parse_menu_file(path) -> list[tuple[str, str, float]]:
    with open(path, 'r') as file:
        menu_string = file.read()
        return parse_menu(menu_string)

def parse_menu(menu_string: str) -> list[tuple[str, str, float]]:
    try:
        parsed_menu = menu_parser.parseString(menu_string)
    except ParseException as err:
        raise ParseError(f"Menu not formatted correctly{err}")
    menu = []
    for cat in parsed_menu:
        cat_name = cat.name[0]
        for (recipe_name, servings) in cat.recipes:
            menu.append((cat_name, recipe_name, servings))
    return menu

def recipe_db(path):
    db = TinyDB('recipe_db.json')
    db.insert_multiple([recipe_dict(parse_recipe(path+"/"+recipe)) for recipe in os.listdir(path) if recipe.endswith(".txt")])