import gettext

i18n = {
    'de': gettext.translation('fettnapf', localedir='locales', languages=['de']),
    'en': gettext.translation('fettnapf', localedir='locales', languages=['en']),
}


def translate_category(category, lang):
    return get_i18n(lang).gettext(category)

def get_languages():
    return list(i18n.keys())

def get_i18n(lang):
    return i18n[lang] if lang in i18n else i18n['de']


categories = {
    "baking": [],
    "cannedgoods": [],
    "breakfast": [],
    "vegetables_fruit": [],
    "beverages": [],
    "spices": [],
    "hygiene": [],
    "chilledgoods": [],
    "nometro": [],
    "oil_vinegar": [],
    "snacks": [],
    "drygoods": [],
}
# add category names of all languages to this dict
for category, names in categories.items():
    for lang in get_languages():
        names.append(i18n[lang].gettext(category).lower())

print(categories)
def category_name_to_id(name):
    """
    takes a category name in any language and maps
    that to an category ID
    (which is mostly just the name in english)
    """
    for category, names in categories.items():
        for lang_name in names:
            if name.lower() == lang_name:
                return category

    # fallback
    return name


# force UTF-8 encoding for xgettext
i18n['en'].gettext("äü¥")


# categories for automatic extraction with xgettext
i18n['en'].gettext("baking")
i18n['en'].gettext("cannedgoods")
i18n['en'].gettext("breakfast")
i18n['en'].gettext("vegetables_fruit")
i18n['en'].gettext("beverages")
i18n['en'].gettext("spices")
i18n['en'].gettext("hygiene")
i18n['en'].gettext("chilledgoods")
i18n['en'].gettext("nometro")
i18n['en'].gettext("oil_vinegar")
i18n['en'].gettext("snacks")
i18n['en'].gettext("drygoods")

i18n['en'].gettext("Misc")
i18n['en'].gettext("Frühstück")
i18n['en'].gettext("Gebäck")
i18n['en'].gettext("Hauptgericht")
i18n['en'].gettext("Salat")
i18n['en'].gettext("Süßkram")
i18n['en'].gettext("Eintopf")
i18n['en'].gettext("Beilage")