from collections import Counter
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
    {"item": "Apă minerală/plată", "cuisine": "universală", "vegan": True, "alergeni": []},
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


guests = [
    {'name': 'Invitat 1', 'cuisine_preference': 'asiatică', 'vegan': True, 'allergens': []} ,
{'name': 'Invitat 2', 'cuisine_preference': 'vegană', 'vegan': False, 'allergens': ['gluten']} ,
{'name': 'Invitat 3', 'cuisine_preference': 'vegană', 'vegan': True, 'allergens': ['ouă']} ,
{'name': 'Invitat 4', 'cuisine_preference': 'spaniolă', 'vegan': False, 'allergens': ['nuci']} ,
{'name': 'Invitat 5', 'cuisine_preference': 'franceză', 'vegan': False, 'allergens': ['pește']} ,
{'name': 'Invitat 6', 'cuisine_preference': 'vegană', 'vegan': True, 'allergens': ['soia']} ,
{'name': 'Invitat 7', 'cuisine_preference': 'românească', 'vegan': False, 'allergens': ['gluten']} ,
{'name': 'Invitat 8', 'cuisine_preference': 'orientală', 'vegan': False, 'allergens': ['gluten']} ,
{'name': 'Invitat 9', 'cuisine_preference': 'asiatică', 'vegan': False, 'allergens': ['pește']} ,
{'name': 'Invitat 10', 'cuisine_preference': 'italiană', 'vegan': True, 'allergens': ['pește']} ,
{'name': 'Invitat 11', 'cuisine_preference': 'asiatică', 'vegan': True, 'allergens': ['soia']} ,
{'name': 'Invitat 12', 'cuisine_preference': 'românească', 'vegan': False, 'allergens': []} ,
{'name': 'Invitat 13', 'cuisine_preference': 'universală', 'vegan': True, 'allergens': ['crustacee']} ,
{'name': 'Invitat 14', 'cuisine_preference': 'italiană', 'vegan': True, 'allergens': ['sulfiți']} ,
{'name': 'Invitat 15', 'cuisine_preference': 'italiană', 'vegan': True, 'allergens': ['sulfiți']} ,
{'name': 'Invitat 16', 'cuisine_preference': 'asiatică', 'vegan': True, 'allergens': ['soia']} ,
{'name': 'Invitat 17', 'cuisine_preference': 'franceză', 'vegan': False, 'allergens': []} ,
{'name': 'Invitat 18', 'cuisine_preference': 'italiană', 'vegan': True, 'allergens': ['gluten']} ,
{'name': 'Invitat 19', 'cuisine_preference': 'italiană', 'vegan': False, 'allergens': ['crustacee']} ,
{'name': 'Invitat 20', 'cuisine_preference': 'orientală', 'vegan': True, 'allergens': ['sulfiți']} ,
{'name': 'Invitat 21', 'cuisine_preference': 'orientală', 'vegan': False, 'allergens': ['lactoză']} ,
{'name': 'Invitat 22', 'cuisine_preference': 'românească', 'vegan': True, 'allergens': ['lactoză']} ,
{'name': 'Invitat 23', 'cuisine_preference': 'vegană', 'vegan': False, 'allergens': ['pește']} ,
{'name': 'Invitat 24', 'cuisine_preference': 'mexicană', 'vegan': True, 'allergens': ['gluten']} ,
{'name': 'Invitat 25', 'cuisine_preference': 'asiatică', 'vegan': False, 'allergens': ['pește']} ,
{'name': 'Invitat 26', 'cuisine_preference': 'orientală', 'vegan': True, 'allergens': []} ,
{'name': 'Invitat 27', 'cuisine_preference': 'grecească', 'vegan': False, 'allergens': ['crustacee']} ,
{'name': 'Invitat 28', 'cuisine_preference': 'grecească', 'vegan': True, 'allergens': ['ouă']} ,
{'name': 'Invitat 29', 'cuisine_preference': 'orientală', 'vegan': True, 'allergens': ['crustacee']} ,
{'name': 'Invitat 30', 'cuisine_preference': 'românească', 'vegan': True, 'allergens': []} ,
{'name': 'Invitat 31', 'cuisine_preference': 'italiană', 'vegan': False, 'allergens': ['pește']} ,
{'name': 'Invitat 32', 'cuisine_preference': 'grecească', 'vegan': False, 'allergens': ['muștar']} ,
{'name': 'Invitat 33', 'cuisine_preference': 'asiatică', 'vegan': True, 'allergens': ['soia']} ,
{'name': 'Invitat 34', 'cuisine_preference': 'românească', 'vegan': False, 'allergens': ['pește']} ,
{'name': 'Invitat 35', 'cuisine_preference': 'asiatică', 'vegan': True, 'allergens': ['pește']} ,
{'name': 'Invitat 36', 'cuisine_preference': 'mexicană', 'vegan': False, 'allergens': ['soia']} ,
{'name': 'Invitat 37', 'cuisine_preference': 'grecească', 'vegan': False, 'allergens': ['lactoză']} ,
{'name': 'Invitat 38', 'cuisine_preference': 'universală', 'vegan': True, 'allergens': ['crustacee']} ,
{'name': 'Invitat 39', 'cuisine_preference': 'mexicană', 'vegan': False, 'allergens': ['sulfiți']} ,
{'name': 'Invitat 40', 'cuisine_preference': 'grecească', 'vegan': True, 'allergens': []} ,
{'name': 'Invitat 41', 'cuisine_preference': 'vegană', 'vegan': True, 'allergens': ['muștar']} ,
{'name': 'Invitat 42', 'cuisine_preference': 'vegană', 'vegan': True, 'allergens': ['nuci']} ,
{'name': 'Invitat 43', 'cuisine_preference': 'grecească', 'vegan': False, 'allergens': ['soia']} ,
{'name': 'Invitat 44', 'cuisine_preference': 'asiatică', 'vegan': False, 'allergens': ['ouă']} ,
{'name': 'Invitat 45', 'cuisine_preference': 'vegană', 'vegan': False, 'allergens': ['gluten']} ,
{'name': 'Invitat 46', 'cuisine_preference': 'franceză', 'vegan': False, 'allergens': ['nuci']} ,
{'name': 'Invitat 47', 'cuisine_preference': 'spaniolă', 'vegan': True, 'allergens': ['pește']} ,
{'name': 'Invitat 48', 'cuisine_preference': 'franceză', 'vegan': False, 'allergens': ['muștar']} ,
{'name': 'Invitat 49', 'cuisine_preference': 'mexicană', 'vegan': True, 'allergens': ['soia']} ,
{'name': 'Invitat 50', 'cuisine_preference': 'românească', 'vegan': True, 'allergens': ['lactoză']} ,
{'name': 'Invitat 51', 'cuisine_preference': 'vegană', 'vegan': False, 'allergens': ['sulfiți']} ,
{'name': 'Invitat 52', 'cuisine_preference': 'orientală', 'vegan': True, 'allergens': ['soia']} ,
{'name': 'Invitat 53', 'cuisine_preference': 'universală', 'vegan': True, 'allergens': ['crustacee']} ,
{'name': 'Invitat 54', 'cuisine_preference': 'spaniolă', 'vegan': False, 'allergens': ['gluten']} ,
{'name': 'Invitat 55', 'cuisine_preference': 'orientală', 'vegan': False, 'allergens': ['ouă']} ,
{'name': 'Invitat 56', 'cuisine_preference': 'asiatică', 'vegan': True, 'allergens': ['lactoză']} ,
{'name': 'Invitat 57', 'cuisine_preference': 'românească', 'vegan': True, 'allergens': []} ,
{'name': 'Invitat 58', 'cuisine_preference': 'spaniolă', 'vegan': True, 'allergens': ['gluten']} ,
{'name': 'Invitat 59', 'cuisine_preference': 'grecească', 'vegan': True, 'allergens': ['soia']} ,
{'name': 'Invitat 60', 'cuisine_preference': 'universală', 'vegan': False, 'allergens': ['crustacee']} ,
{'name': 'Invitat 61', 'cuisine_preference': 'italiană', 'vegan': False, 'allergens': ['sulfiți']} ,
{'name': 'Invitat 62', 'cuisine_preference': 'franceză', 'vegan': True, 'allergens': ['crustacee']} ,
{'name': 'Invitat 63', 'cuisine_preference': 'spaniolă', 'vegan': False, 'allergens': ['soia']} ,
{'name': 'Invitat 64', 'cuisine_preference': 'grecească', 'vegan': False, 'allergens': ['muștar']} ,
{'name': 'Invitat 65', 'cuisine_preference': 'spaniolă', 'vegan': True, 'allergens': ['gluten']} ,
{'name': 'Invitat 66', 'cuisine_preference': 'universală', 'vegan': True, 'allergens': ['sulfiți']} ,
{'name': 'Invitat 67', 'cuisine_preference': 'românească', 'vegan': True, 'allergens': ['nuci']} ,
{'name': 'Invitat 68', 'cuisine_preference': 'franceză', 'vegan': True, 'allergens': ['gluten']} ,
{'name': 'Invitat 69', 'cuisine_preference': 'mexicană', 'vegan': False, 'allergens': ['muștar']} ,
{'name': 'Invitat 70', 'cuisine_preference': 'orientală', 'vegan': True, 'allergens': []} ,
{'name': 'Invitat 71', 'cuisine_preference': 'franceză', 'vegan': False, 'allergens': ['sulfiți']} ,
{'name': 'Invitat 72', 'cuisine_preference': 'vegană', 'vegan': False, 'allergens': ['muștar']} ,
{'name': 'Invitat 73', 'cuisine_preference': 'italiană', 'vegan': True, 'allergens': ['pește']} ,
{'name': 'Invitat 74', 'cuisine_preference': 'românească', 'vegan': False, 'allergens': ['crustacee']} ,
{'name': 'Invitat 75', 'cuisine_preference': 'franceză', 'vegan': False, 'allergens': ['soia']} ,
{'name': 'Invitat 76', 'cuisine_preference': 'universală', 'vegan': False, 'allergens': ['muștar']} ,
{'name': 'Invitat 77', 'cuisine_preference': 'italiană', 'vegan': False, 'allergens': ['ouă']} ,
{'name': 'Invitat 78', 'cuisine_preference': 'asiatică', 'vegan': True, 'allergens': ['crustacee']} ,
{'name': 'Invitat 79', 'cuisine_preference': 'universală', 'vegan': True, 'allergens': ['crustacee']} ,
{'name': 'Invitat 80', 'cuisine_preference': 'mexicană', 'vegan': True, 'allergens': ['muștar']} ,
{'name': 'Invitat 81', 'cuisine_preference': 'orientală', 'vegan': False, 'allergens': ['nuci']} ,
{'name': 'Invitat 82', 'cuisine_preference': 'universală', 'vegan': False, 'allergens': ['sulfiți']} ,
{'name': 'Invitat 83', 'cuisine_preference': 'grecească', 'vegan': False, 'allergens': ['muștar']} ,
{'name': 'Invitat 84', 'cuisine_preference': 'asiatică', 'vegan': False, 'allergens': ['muștar']} ,
{'name': 'Invitat 85', 'cuisine_preference': 'spaniolă', 'vegan': False, 'allergens': ['lactoză']} ,
{'name': 'Invitat 86', 'cuisine_preference': 'vegană', 'vegan': True, 'allergens': ['crustacee']} ,
{'name': 'Invitat 87', 'cuisine_preference': 'italiană', 'vegan': False, 'allergens': ['gluten']} ,
{'name': 'Invitat 88', 'cuisine_preference': 'universală', 'vegan': True, 'allergens': ['lactoză']} ,
{'name': 'Invitat 89', 'cuisine_preference': 'mexicană', 'vegan': True, 'allergens': ['nuci']} ,
{'name': 'Invitat 90', 'cuisine_preference': 'românească', 'vegan': False, 'allergens': ['ouă']} ,
{'name': 'Invitat 91', 'cuisine_preference': 'italiană', 'vegan': True, 'allergens': ['gluten']} ,
{'name': 'Invitat 92', 'cuisine_preference': 'grecească', 'vegan': True, 'allergens': ['muștar']} ,
{'name': 'Invitat 93', 'cuisine_preference': 'grecească', 'vegan': False, 'allergens': ['lactoză']} ,
{'name': 'Invitat 94', 'cuisine_preference': 'mexicană', 'vegan': False, 'allergens': ['gluten']} ,
{'name': 'Invitat 95', 'cuisine_preference': 'orientală', 'vegan': True, 'allergens': ['lactoză']} ,
{'name': 'Invitat 96', 'cuisine_preference': 'franceză', 'vegan': False, 'allergens': ['soia']} ,
{'name': 'Invitat 97', 'cuisine_preference': 'vegană', 'vegan': True, 'allergens': ['ouă']} ,
{'name': 'Invitat 98', 'cuisine_preference': 'orientală', 'vegan': False, 'allergens': ['sulfiți']} ,
{'name': 'Invitat 99', 'cuisine_preference': 'românească', 'vegan': True, 'allergens': ['ouă']} ,
{'name': 'Invitat 100', 'cuisine_preference': 'spaniolă', 'vegan': True, 'allergens': []} 
]

count = 0
majority_allergens = []

for guest in guests:
    if guest["vegan"] == True:
        count += 1
    for alergen in guest["allergens"]:
        majority_allergens.append(alergen)

allergen_counts = Counter(majority_allergens)
menu_selected = []

for guest in guests:
    print(f"Generând meniul pentru {guest['name']}:")
    
    available_dishes = [dish for dish in menu if dish["cuisine"] == guest["cuisine_preference"]]
    
    if guest["vegan"]:
        available_dishes = [dish for dish in available_dishes if dish["vegan"]]

    for allergen in guest["allergens"]:
        available_dishes = [dish for dish in available_dishes if allergen not in dish["alergeni"]]
    
    if available_dishes:
        selected_dish = available_dishes[0]
        menu_selected.append(selected_dish)
        print(f"  - Selecționat: {selected_dish['item']}")
    else:
        print("  - Nu există preparate disponibile pentru acest invitat.")


unique_menu = []
seen = set()

for dish in menu_selected:
    if dish['item'] not in seen:
        unique_menu.append(dish)
        seen.add(dish['item'])


invitati = 0
for guest in guests:
    invitati += 1


with open("meniu_generat.txt", "a", encoding="utf-8") as f:
    f.write(f"\nMeniul complet generat pentru {invitati} invitați:\n")
    for dish in unique_menu:
        f.write(f"- {dish['item']} ({dish['cuisine']} - {'Vegan' if dish['vegan'] else 'Non-Vegan'}, alergeni: {', '.join(dish['alergeni'])if dish['alergeni'] else "Nu contine"})\n")
