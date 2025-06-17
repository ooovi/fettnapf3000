
category_names = {
    "backen": { "en": "baking" },
    "dosen": { "en": "canned goods" },
    "frühstück": { "en": "breakfast" },
    "gemüse/obst": { "en": "vegetables/fruit" },
    "getränke": { "en": "beverages" },
    "gewürze": { "en": "spices" },
    "hygiene": { "en": "hygiene" },
    "kühlware": { "en": "chilled goods" },
    "nometro": { "en": "nometro" },
    "öl/essig": { "en": "oil/vinegar" },
    "snacks": { "en": "snacks" },
    "trockenware": { "en": "dry goods" },
}

def translate_category(category, lang):
    if category in category_names:
        if lang in category_names[category]:
            return category_names[category][lang]
    return category