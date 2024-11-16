import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistem_inteligent_de_gestionare_a_evenimentelor.settings')
import django
django.setup()
from base.models import Menu

menu = [
    {"item": "Guacamole cu nachos", "cuisine": "mexicană", "vegan": True, "alergeni": ["gluten"]},
    {"item": "Tacos cu carne de vită", "cuisine": "mexicană", "vegan": False, "alergeni": ["gluten"]},
    {"item": "Falafel cu humus", "cuisine": "orientală", "vegan": True, "alergeni": ["soia"]},
    {"item": "Tabbouleh cu lămâie", "cuisine": "orientală", "vegan": True, "alergeni": []},
    {"item": "Paella cu fructe de mare", "cuisine": "spaniolă", "vegan": False, "alergeni": ["pește", "crustacee"]},
    {"item": "Croissant cu ciocolată", "cuisine": "franceză", "vegan": False, "alergeni": ["gluten", "lactoză"]},
    {"item": "Quiche cu spanac și brânză", "cuisine": "franceză", "vegan": False, "alergeni": ["gluten", "lactoză"]},
    {"item": "Moussaka cu carne de miel", "cuisine": "grecească", "vegan": False, "alergeni": ["gluten", "lactoză"]},
    {"item": "Focaccia cu rozmarin", "cuisine": "italiană", "vegan": True, "alergeni": ["gluten"]},
    {"item": "Pasta carbonara", "cuisine": "italiană", "vegan": False, "alergeni": ["gluten", "lactoză", "ouă"]}
]

for dish in menu:
    Menu.objects.create(
        item_name=dish["item"],
        item_cuisine=dish["cuisine"],
        item_vegan=dish["vegan"],
        allergens=dish["alergeni"]
    )
