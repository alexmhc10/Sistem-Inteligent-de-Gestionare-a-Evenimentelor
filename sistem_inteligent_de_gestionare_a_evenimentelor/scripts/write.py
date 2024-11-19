from ...base.models import Menu

menu = [
    {"item": "Bruschete cu roșii și busuioc", "cuisine": "italiană", "vegan": True, "alergeni": ["gluten"]},
    {"item": "Platou de brânzeturi și fructe", "cuisine": "românească", "vegan": False, "alergeni": ["lactoză"]},
    {"item": "Spring rolls cu legume", "cuisine": "asiatică", "vegan": True, "alergeni": ["gluten", "soia"]},
    {"item": "Rulouri de șuncă cu hrean", "cuisine": "românească", "vegan": False, "alergeni": ["lactoză"]},
    {"item": "Chifteluțe marinate", "cuisine": "românească", "vegan": False, "alergeni": ["gluten", "ouă"]},
    {"item": "Mini sandwich-uri cu somon", "cuisine": "italiană", "vegan": False, "alergeni": ["gluten", "pește"]},
    {"item": "Sushi rolls cu avocado", "cuisine": "asiatică", "vegan": True, "alergeni": ["gluten", "soia"]},
    {"item": "Frigărui de legume", "cuisine": "vegană", "vegan": True, "alergeni": []},
    {"item": "Sarmale cu mămăligă", "cuisine": "românească", "vegan": False, "alergeni": ["gluten"]},
    {"item": "Lasagna cu legume", "cuisine": "italiană", "vegan": True, "alergeni": ["gluten", "lactoză"]},
    {"item": "Pui teriyaki", "cuisine": "asiatică", "vegan": False, "alergeni": ["gluten", "soia"]},
    {"item": "Burger vegan de năut", "cuisine": "vegană", "vegan": True, "alergeni": ["gluten"]},
    {"item": "Risotto cu șofran", "cuisine": "italiană", "vegan": False, "alergeni": ["lactoză"]},
    {"item": "Tofu cu legume la wok", "cuisine": "asiatică", "vegan": True, "alergeni": ["soia"]},
    {"item": "Gulaș de vită", "cuisine": "românească", "vegan": False, "alergeni": ["gluten"]},
    {"item": "Paste bolognese", "cuisine": "italiană", "vegan": False, "alergeni": ["gluten"]},
    {"item": "Cheesecake cu fructe de pădure", "cuisine": "italiană", "vegan": False, "alergeni": ["gluten", "lactoză", "ouă"]},
    {"item": "Brownie vegan", "cuisine": "vegană", "vegan": True, "alergeni": ["gluten", "soia"]},
    {"item": "Prăjitură cu mere", "cuisine": "românească", "vegan": True, "alergeni": ["gluten"]},
    {"item": "Mochi cu înghețată", "cuisine": "asiatică", "vegan": False, "alergeni": ["lactoză"]},
    {"item": "Cocktail Aperol Spritz", "cuisine": "italiană", "vegan": True, "alergeni": []},
    {"item": "Vin alb/roșu", "cuisine": "universală", "vegan": True, "alergeni": ["sulfiți"]},
    {"item": "Bere artizanală", "cuisine": "universală", "vegan": False, "alergeni": ["gluten"]},
    {"item": "Sucuri naturale", "cuisine": "universală", "vegan": True, "alergeni": []},
    {"item": "Apă minerală/plată", "cuisine": "universală", "vegan": True, "alergeni": []}
]

for dish in menu:
    Menu.objects.create(
        item_name=dish["item"],
        item_cuisine=dish["cuisine"],
        item_vegan=dish["vegan"],
        allergens=dish["alergeni"]
    )
