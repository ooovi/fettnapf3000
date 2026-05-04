import sys
import os
import json

from tinydb import TinyDB
import cherrypy

from recipe import Recipe, recipe_string,recipe_dict
from pages.fettnapf import FettnapfPage
from pages.repertoire import RepertoirePage
from pages.recipe import RecipePage

from metrodb import metrodb

db = {"team": TinyDB(f'../../fettnapf3000recipes/team_recipes.json', indent=2),
      "food4action": TinyDB(f'../../fettnapf3000recipes/food4action_recipes.json', indent=2),
      "cutiemeow": TinyDB(f'../../fettnapf3000recipes/cutiemeow_recipes.json', indent=2)}


TEAM_USERS = json.load(open("users.txt"))
F4A_USERS = json.load(open("f4a_users.txt"))
CUTIEMEOW_USERS = json.load(open("cutiemeow_users.txt"))
KEY = open("key.txt").read()

if __name__ == '__main__':
    if len(sys.argv) == 3:
        cherrypy.config.update({'server.socket_host': sys.argv[1],
                                'server.socket_port': int(sys.argv[2]),
                               })
    if len(sys.argv) == 2:
        cherrypy.config.update({'server.socket_port': int(sys.argv[1])})
    conf = {
        '/': {
            'tools.sessions.on': False,
            'tools.staticdir.root': os.path.abspath(os.getcwd())
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './public'
        },
        '/repertoire': {
            'tools.auth_digest.on': True,
            'tools.auth_digest.realm': 'localhost',
            'tools.auth_digest.get_ha1': cherrypy.lib.auth_digest.get_ha1_dict_plain(TEAM_USERS),
            'tools.auth_digest.key': KEY,
            'tools.auth_digest.accept_charset': 'UTF-8',
         },
         '/food4action/repertoire': {
            'tools.auth_digest.on': True,
            'tools.auth_digest.realm': 'localhost',
            'tools.auth_digest.get_ha1': cherrypy.lib.auth_digest.get_ha1_dict_plain(F4A_USERS),
            'tools.auth_digest.key': KEY,
            'tools.auth_digest.accept_charset': 'UTF-8',
         },
         '/cutiemeow/repertoire': {
            'tools.auth_digest.on': True,
            'tools.auth_digest.realm': 'localhost',
            'tools.auth_digest.get_ha1': cherrypy.lib.auth_digest.get_ha1_dict_plain(CUTIEMEOW_USERS),
            'tools.auth_digest.key': KEY,
            'tools.auth_digest.accept_charset': 'UTF-8',
         }
    }

    root = RecipePage(db)
    root.team = RecipePage(db, "team")
    root.repertoire = RepertoirePage(db)

    root.food4action = RecipePage(db, "food4action")
    root.food4action.repertoire = RepertoirePage(db, "food4action")

    root.cutiemeow = RecipePage(db, "cutiemeow")
    root.cutiemeow.repertoire = RepertoirePage(db, "cutiemeow")

    cherrypy.quickstart(root, config = conf)
