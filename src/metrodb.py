from tinydb import TinyDB
from tinydb.storages import MemoryStorage

# an in-memory database of all known ingredients
entries = [
    {"english": "coconut milk"                 , "category": "nometro"     , "ingredient" : "kokosmilch"                      },
    {"english": "kala namak salt"              , "category": "nometro"     , "ingredient" : "kala namak (eiersalz)"           },
    {"english": "coconut oil"                  , "category": "nometro"     , "ingredient" : "kokosfett"                       },
    {"english": "black olives"                 , "category": "nometro"     , "ingredient" : "schwarze oliven"                 },
    {"english": "nutritional yeast"            , "category": "nometro"     , "ingredient" : "hefeflocken"                     },
    {"english": "light soy sauce (gluten free)", "category": "nometro"     , "ingredient" : "helle sojasauce (glutenfrei)"    },
    {"english": "peanut butter"                , "category": "nometro"     , "ingredient" : "erdnussbutter"                   },
    {"english": "black sesame seeds"           , "category": "nometro"     , "ingredient" : "schwarzer sesam"                 },
    {"english": "sticky rice"                  , "category": "nometro"     , "ingredient" : "klebreis"                        },
    {"english": "soy chunks"                   , "category": "nometro"     , "ingredient" : "soja chunks"                     },
    {"english": "tempeh"                       , "category": "nometro"     , "ingredient" : "tempeh"                          },
    {"english": "tahini"                       , "category": "nometro"     , "ingredient" : "tahin"                           },
    {"english": "miso"                         , "category": "nometro"     , "ingredient" : "miso"                            },
    {"english": "tofu"                         , "category": "nometro"     , "ingredient" : "tofu"                            },
    {"english": "tempe"                        , "category": "nometro"     , "ingredient" : "tempe"                           },
    {"english": "soy bean sprouts"             , "category": "nometro"     , "ingredient" : "sojasprossen"                    },
    {"english": "whear gluten powder"          , "category": "nometro"     , "ingredient" : "seitanpulver"                    },
    {"english": "gas"                          , "category": "hygiene"     , "ingredient" : "gas"                             },
    {"english": "disinfectant"                 , "category": "hygiene"     , "ingredient" : "desi"                            },
    {"english": "trash bags"                   , "category": "hygiene"     , "ingredient" : "müllbeutel"                      },
    {"english": "sponges"                      , "category": "hygiene"     , "ingredient" : "schwämme"                        },
    {"english": "lappen"                       , "category": "hygiene"     , "ingredient" : "lappen"                          },
    {"english": "steel wool"                   , "category": "hygiene"     , "ingredient" : "stahlwolle"                      },
    {"english": "paper towels"                 , "category": "hygiene"     , "ingredient" : "küchenrolle"                     },
    {"english": "dishwashing soap"             , "category": "hygiene"     , "ingredient" : "spüli"                           },
    {"english": "hand soap"                    , "category": "hygiene"     , "ingredient" : "handseife"                       },
    {"english": "rubber gloves"                , "category": "hygiene"     , "ingredient" : "gummihandschuhe"                 },
    {"english": "dishwashing gloves"           , "category": "hygiene"     , "ingredient" : "spülhandschuhe"                  },
    {"english": "baking sheets"                , "category": "hygiene"     , "ingredient" : "backpapier"                      },
    {"english": "red wine"                     , "category": "getränke"    , "ingredient" : "rotwein"                         },
    {"english": "white wine"                   , "category": "getränke"    , "ingredient" : "weißwein"                        },
    {"english": "vodka"                        , "category": "getränke"    , "ingredient" : "wodka"                           },
    {"english": "tomatos"                      , "category": "gemüse/obst" , "ingredient" : "tomaten"                         },
    {"english": "tomatoes"                     , "category": "gemüse/obst" , "ingredient" : "tomaten"                         },
    {"english": "cucumber"                     , "category": "gemüse/obst" , "ingredient" : "gurke"                           },
    {"english": "mushrooms"                    , "category": "gemüse/obst" , "ingredient" : "champis"                         },
    {"english": "savoy cabbage"                , "category": "gemüse/obst" , "ingredient" : "wirsing"                         },
    {"english": "white cabbage"                , "category": "gemüse/obst" , "ingredient" : "weißkohl"                        },
    {"english": "carrots"                      , "category": "gemüse/obst" , "ingredient" : "möhren"                          },
    {"english": "fresh spinach"                , "category": "gemüse/obst" , "ingredient" : "frischer spinat"                 },
    {"english": "fresh mint"                   , "category": "gemüse/obst" , "ingredient" : "frische minze"                   },
    {"english": "fresh parsley"                , "category": "gemüse/obst" , "ingredient" : "frische petersilie"              },
    {"english": "spring onions"                , "category": "gemüse/obst" , "ingredient" : "frühlingszwiebeln"               },
    {"english": "fresh dill"                   , "category": "gemüse/obst" , "ingredient" : "frischer dill"                   },
    {"english": "fresh chives"                 , "category": "gemüse/obst" , "ingredient" : "frischer schnittlauch"           },
    {"english": "onions"                       , "category": "gemüse/obst" , "ingredient" : "zwiebeln"                        },
    {"english": "red onions"                   , "category": "gemüse/obst" , "ingredient" : "rote zwiebeln"                   },
    {"english": "garlic"                       , "category": "gemüse/obst" , "ingredient" : "knobi"                           },
    {"english": "salad"                        , "category": "gemüse/obst" , "ingredient" : "salat"                           },
    {"english": "rucola"                       , "category": "gemüse/obst" , "ingredient" : "rucola"                          },
    {"english": "snack veggies"                , "category": "gemüse/obst" , "ingredient" : "snäckgemüse"                     },
    {"english": "fryable veggies"              , "category": "gemüse/obst" , "ingredient" : "bratgemüse"                      },
    {"english": "fruit"                        , "category": "gemüse/obst" , "ingredient" : "obst"                            },
    {"english": "apples"                       , "category": "gemüse/obst" , "ingredient" : "äpfel"                           },
    {"english": "pears"                        , "category": "gemüse/obst" , "ingredient" : "birnen"                          },
    {"english": "lime"                         , "category": "gemüse/obst" , "ingredient" : "limetten"                        },
    {"english": "lemon"                        , "category": "gemüse/obst" , "ingredient" : "zitronen"                        },
    {"english": "organic orange"               , "category": "gemüse/obst" , "ingredient" : "bio-orangen"                     },
    {"english": "sweet potatos"                , "category": "gemüse/obst" , "ingredient" : "süßkartoffeln"                   },
    {"english": "potatos"                      , "category": "gemüse/obst" , "ingredient" : "kartoffeln"                      },
    {"english": "brokkoli"                     , "category": "gemüse/obst" , "ingredient" : "brokkoli"                        },
    {"english": "green beans"                  , "category": "gemüse/obst" , "ingredient" : "grüne bohnen"                    },
    {"english": "ginger"                       , "category": "gemüse/obst" , "ingredient" : "ingwer"                          },
    {"english": "pumpkin"                      , "category": "gemüse/obst" , "ingredient" : "kürbis"                          },
    {"english": "bell pepper"                  , "category": "gemüse/obst" , "ingredient" : "paprika"                         },
    {"english": "celery"                       , "category": "gemüse/obst" , "ingredient" : "sellerie"                        },
    {"english": "butternut pumpkin"            , "category": "gemüse/obst" , "ingredient" : "butternutkürbis"                 },
    {"english": "leek"                         , "category": "gemüse/obst" , "ingredient" : "lauch"                           },
    {"english": "beetroot (fresh)"             , "category": "gemüse/obst" , "ingredient" : "rote beete (roh)"                },
    {"english": "canned tomatos (chopped)"     , "category": "dosen"       , "ingredient" : "dosentomaten (gehackt)"          },
    {"english": "canned tomatos (paste)"       , "category": "dosen"       , "ingredient" : "dosentomaten (passiert)"         },
    {"english": "tomato concentrate"           , "category": "dosen"       , "ingredient" : "tomatenmark"                     },
    {"english": "pickled cucumber"             , "category": "dosen"       , "ingredient" : "saure gurken"                    },
    {"english": "canned sweet corn"            , "category": "dosen"       , "ingredient" : "dosenmais"                       },
    {"english": "canned green peas"            , "category": "dosen"       , "ingredient" : "dosenerbsen"                     },
    {"english": "canned black beans"           , "category": "dosen"       , "ingredient" : "schwarze bohnen (dose)"          },
    {"english": "beetroot (pre-cooked)"        , "category": "dosen"       , "ingredient" : "rote beete (gekocht)"            },
    {"english": "baked beans"                  , "category": "dosen"       , "ingredient" : "baked beans"                     },
    {"english": "sauerkraut"                   , "category": "dosen"       , "ingredient" : "sauerkraut"                      },
    {"english": "applesauce"                   , "category": "dosen"       , "ingredient" : "apfelmus"                        },
    {"english": "cane sugar"                   , "category": "backen"      , "ingredient" : "rohrzucker"                      },
    {"english": "flour"                        , "category": "backen"      , "ingredient" : "mehl"                            },
    {"english": "cornstarch"                   , "category": "backen"      , "ingredient" : "stärke"                          },
    {"english": "natron"                       , "category": "backen"      , "ingredient" : "natron"                          },
    {"english": "dry yeast"                    , "category": "backen"      , "ingredient" : "trockenhefe"                     },
    {"english": "sugar"                        , "category": "backen"      , "ingredient" : "zucker"                          },
    {"english": "cocoa powder"                 , "category": "backen"      , "ingredient" : "kakao"                           },
    {"english": "chocolate"                    , "category": "backen"      , "ingredient" : "kuvertüre/schoki vegan"          },
    {"english": "vanilla sugar"                , "category": "backen"      , "ingredient" : "vanillezucker"                   },
    {"english": "sugar unicorns"               , "category": "backen"      , "ingredient" : "zuckereinhörner"                 },
    {"english": "powdered sugar"               , "category": "backen"      , "ingredient" : "puderzucker"                     },
    {"english": "ground hazelnuts"             , "category": "backen"      , "ingredient" : "gemahlene haselnüsse"            },
    {"english": "baking powder"                , "category": "backen"      , "ingredient" : "backpulver"                      },
    {"english": "olive oil"                    , "category": "öl/essig"    , "ingredient" : "olivenöl"                        },
    {"english": "linseed oil"                  , "category": "öl/essig"    , "ingredient" : "leinöl"                          },
    {"english": "oil"                          , "category": "öl/essig"    , "ingredient" : "öl"                              },
    {"english": "balsamico"                    , "category": "öl/essig"    , "ingredient" : "balsamico"                       },
    {"english": "balsamico (white)"            , "category": "öl/essig"    , "ingredient" : "balsamico (hell)"                },
    {"english": "lemon juice"                  , "category": "öl/essig"    , "ingredient" : "zitronensaft"                    },
    {"english": "apple cider vinegar"          , "category": "öl/essig"    , "ingredient" : "apfelessig"                      },
    {"english": "white wine vinegar"           , "category": "öl/essig"    , "ingredient" : "weißweinessig"                   },
    {"english": "laurel leaves"                , "category": "gewürze"     , "ingredient" : "lorbeer"                         },
    {"english": "pepper"                       , "category": "gewürze"     , "ingredient" : "pfeffer"                         },
    {"english": "pepper whole"                 , "category": "gewürze"     , "ingredient" : "pfeffer ganz"                    },
    {"english": "salt"                         , "category": "gewürze"     , "ingredient" : "salz"                            },
    {"english": "mustard"                      , "category": "gewürze"     , "ingredient" : "senf"                            },
    {"english": "nutmeg"                       , "category": "gewürze"     , "ingredient" : "muskat"                          },
    {"english": "smoked paprika"               , "category": "gewürze"     , "ingredient" : "geräuchertes paprikapulver"      },
    {"english": "cumin"                        , "category": "gewürze"     , "ingredient" : "kreuzkümmel"                     },
    {"english": "thyme"                        , "category": "gewürze"     , "ingredient" : "thymian"                         },
    {"english": "caraway"                      , "category": "gewürze"     , "ingredient" : "kümmel"                          },
    {"english": "vanilla"                      , "category": "gewürze"     , "ingredient" : "vanille"                         },
    {"english": "black onion seeds"            , "category": "gewürze"     , "ingredient" : "schwarzkümmel"                   },
    {"english": "turmeric"                     , "category": "gewürze"     , "ingredient" : "kurkuma"                         },
    {"english": "cinnamon"                     , "category": "gewürze"     , "ingredient" : "zimt"                            },
    {"english": "oregano"                      , "category": "gewürze"     , "ingredient" : "oregano"                         },
    {"english": "rosemary"                     , "category": "gewürze"     , "ingredient" : "rosmarin"                        },
    {"english": "allspice"                     , "category": "gewürze"     , "ingredient" : "allspice"                        },
    {"english": "curry powder"                 , "category": "gewürze"     , "ingredient" : "curry (pulver)"                  },
    {"english": "paprika powder"               , "category": "gewürze"     , "ingredient" : "paprika (pulver)"                },
    {"english": "chili powder"                 , "category": "gewürze"     , "ingredient" : "chili (pulver)"                  },
    {"english": "ginger powder"                , "category": "gewürze"     , "ingredient" : "ingwer (pulver)"                 },
    {"english": "vegetable broth"              , "category": "gewürze"     , "ingredient" : "gemüsebrühe"                     },
    {"english": "sojahack (dry)"               , "category": "trockenware" , "ingredient" : "sojahack (trocken)"              },
    {"english": "lasagna sheets"               , "category": "trockenware" , "ingredient" : "lasagneplatten"                  },
    {"english": "pasta"                        , "category": "trockenware" , "ingredient" : "pasta"                           },
    {"english": "couscous"                     , "category": "trockenware" , "ingredient" : "couscous"                        },
    {"english": "grünkern"                     , "category": "trockenware" , "ingredient" : "grünkern"                        },
    {"english": "basmati"                      , "category": "trockenware" , "ingredient" : "basmati"                         },
    {"english": "brown lentils"                , "category": "trockenware" , "ingredient" : "braune linsen (tellerlinsen)"    },
    {"english": "red lentils"                  , "category": "trockenware" , "ingredient" : "rote linsen"                     },
    {"english": "sunflower seeds"              , "category": "trockenware" , "ingredient" : "sonnenblumenkerne"               },
    {"english": "kidney beans (dry, wet x 4)"  , "category": "trockenware" , "ingredient" : "kidneybohnen (trocken, nass x 4)"},
    {"english": "white beans (dry, wet x 4)"   , "category": "trockenware" , "ingredient" : "weiße bohnen (trocken, nass x 4)"},
    {"english": "chickpeas (dry, wet x 2)"     , "category": "trockenware" , "ingredient" : "kichererbsen (trocken, nass x 2)"},
    {"english": "capers"                       , "category": "trockenware" , "ingredient" : "kapern"                          },
    {"english": "dried tomatos in oil"         , "category": "trockenware" , "ingredient" : "getrocknete tomaten in öl"       },
    {"english": "oats"                         , "category": "frühstück"   , "ingredient" : "haferflocken"                    },
    {"english": "vegan sugar cereals"          , "category": "frühstück"   , "ingredient" : "veganes zuckermüsli"             },
    {"english": "coffee"                       , "category": "frühstück"   , "ingredient" : "kaffe"                           },
    {"english": "black tea"                    , "category": "frühstück"   , "ingredient" : "schwarztee"                      },
    {"english": "herbal tea"                   , "category": "frühstück"   , "ingredient" : "kräutertee"                      },
    {"english": "jam"                          , "category": "frühstück"   , "ingredient" : "marmelade"                       },
    {"english": "rose jam"                     , "category": "frühstück"   , "ingredient" : "rosenmarmelade"                  },
    {"english": "bread"                        , "category": "frühstück"   , "ingredient" : "brot"                            },
    {"english": "smoked tofu"                  , "category": "kühlware"    , "ingredient" : "räuchertofu"                     },
    {"english": "sausages"                     , "category": "kühlware"    , "ingredient" : "würstchen"                       },
    {"english": "potato dumpling dough"        , "category": "kühlware"    , "ingredient" : "kloßteig"                        },
    {"english": "tk-rösti"                     , "category": "kühlware"    , "ingredient" : "tk-rösti"                        },
    {"english": "margerine"                    , "category": "kühlware"    , "ingredient" : "margerine"                       },
    {"english": "margerine (small packs)"      , "category": "kühlware"    , "ingredient" : "margerine (kleine packungen)"    },
    {"english": "soy milk"                     , "category": "kühlware"    , "ingredient" : "sojamilch"                       },
    {"english": "soy cream"                    , "category": "kühlware"    , "ingredient" : "sojasahne"                       },
    {"english": "soy yoghurt"                  , "category": "kühlware"    , "ingredient" : "sojajoghurt"                     },
    {"english": "oat milk"                     , "category": "kühlware"    , "ingredient" : "hafermilch"                      },
    {"english": "genuss-block"                 , "category": "kühlware"    , "ingredient" : "genuss-block"                    },
    {"english": "fresh yeast"                  , "category": "kühlware"    , "ingredient" : "frische hefe"                    },
    {"english": "crewcare"                     , "category": "snacks"      , "ingredient" : "crewcare"                        },
    {"english": "puffed rice cakes"            , "category": "snacks"      , "ingredient" : "reiswaffeln"                     },
    {"english": "crisps"                       , "category": "snacks"      , "ingredient" : "chips"                           },
    {"english": "pecans"                       , "category": "snacks"      , "ingredient" : "pekannüsse"                      },
    {"english": "walnuts"                      , "category": "snacks"      , "ingredient" : "walnüsse"                        },
    {"english": "peanuts"                      , "category": "snacks"      , "ingredient" : "erdnüsse"                        },
    {"english": "cashew nuts"                  , "category": "snacks"    , "ingredient" : "cashewnüsse"                     },
    ]

metrodb = TinyDB(storage=MemoryStorage)
metrodb.insert_multiple(entries)

def cat_sort(cat: str):
    categories = {
      "hygiene"    : 1,
      "getränke"   : 2,
      "gemüse/obst"  : 3,
      "baking"     : 4,
      "gewürze/öl" : 5,
      "oils"       : 6,
      "cans"       : 7,
      "trockenware": 8,
      "milk"       : 9,
      "frühstück"  : 10,
      "snacks"     : 11,
      "nometro"    : 100,
    }
    if cat in categories:
        return categories[cat]
    else:
        return 0
