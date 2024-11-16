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
    {"item": "Apă minerală/plată", "cuisine": "universală", "vegan": True, "alergeni": []}
]


guests = [
    {"name": "Invitat 1", "cuisine_preference": "universală", "vegan": False, "allergens": ["gluten", "lactoză"]},
    {"name": "Invitat 2", "cuisine_preference": "universală", "vegan": True, "allergens": []},
    {"name": "Invitat 3", "cuisine_preference": "universală", "vegan": False, "allergens": ["soia"]},
    {"name": "Invitat 4", "cuisine_preference": "universală", "vegan": True, "allergens": ["nuci"]},
    {"name": "Invitat 5", "cuisine_preference": "universală", "vegan": False, "allergens": ["ouă", "muștar"]},
    {"name": "Invitat 6", "cuisine_preference": "universală", "vegan": False, "allergens": ["lactoză"]},
    {"name": "Invitat 7", "cuisine_preference": "asiatică", "vegan": True, "allergens": ["gluten"]},
    {"name": "Invitat 8", "cuisine_preference": "vegană", "vegan": True, "allergens": []},
    {"name": "Invitat 9", "cuisine_preference": "românească", "vegan": False, "allergens": ["gluten", "soia"]},
    {"name": "Invitat 10", "cuisine_preference": "italiană", "vegan": False, "allergens": ["ouă", "lactoză"]},
    {"name": "Invitat 11", "cuisine_preference": "asiatică", "vegan": True, "allergens": ["pește"]},
    {"name": "Invitat 12", "cuisine_preference": "vegană", "vegan": True, "allergens": ["soia"]},
    {"name": "Invitat 13", "cuisine_preference": "românească", "vegan": False, "allergens": ["nuci", "muștar"]},
    {"name": "Invitat 14", "cuisine_preference": "italiană", "vegan": True, "allergens": ["gluten"]},
    {"name": "Invitat 15", "cuisine_preference": "asiatică", "vegan": False, "allergens": ["ouă"]},
    {"name": "Invitat 16", "cuisine_preference": "vegană", "vegan": True, "allergens": ["nuci", "soia"]},
    {"name": "Invitat 17", "cuisine_preference": "românească", "vegan": False, "allergens": ["lactoză"]},
    {"name": "Invitat 18", "cuisine_preference": "italiană", "vegan": True, "allergens": []},
    {"name": "Invitat 19", "cuisine_preference": "asiatică", "vegan": False, "allergens": ["gluten", "ouă"]},
    {"name": "Invitat 20", "cuisine_preference": "vegană", "vegan": True, "allergens": ["nuci"]},
    {"name": "Invitat 21", "cuisine_preference": "românească", "vegan": False, "allergens": ["muștar", "lactoză"]},
    {"name": "Invitat 22", "cuisine_preference": "italiană", "vegan": False, "allergens": ["gluten"]},
    {"name": "Invitat 23", "cuisine_preference": "asiatică", "vegan": True, "allergens": ["soia"]},
    {"name": "Invitat 24", "cuisine_preference": "vegană", "vegan": True, "allergens": []},
    {"name": "Invitat 25", "cuisine_preference": "românească", "vegan": False, "allergens": ["gluten", "ouă"]},
    {"name": "Invitat 26", "cuisine_preference": "italiană", "vegan": False, "allergens": ["nuci"]},
    {"name": "Invitat 27", "cuisine_preference": "asiatică", "vegan": False, "allergens": ["pește"]},
    {"name": "Invitat 28", "cuisine_preference": "vegană", "vegan": True, "allergens": ["soia", "lactoză"]},
    {"name": "Invitat 29", "cuisine_preference": "românească", "vegan": False, "allergens": []},
    {"name": "Invitat 30", "cuisine_preference": "italiană", "vegan": True, "allergens": ["gluten"]},
    {"name": "Invitat 31", "cuisine_preference": "asiatică", "vegan": True, "allergens": ["soia", "ouă"]},
    {"name": "Invitat 32", "cuisine_preference": "vegană", "vegan": True, "allergens": []},
    {"name": "Invitat 33", "cuisine_preference": "românească", "vegan": False, "allergens": ["muștar"]},
    {"name": "Invitat 34", "cuisine_preference": "italiană", "vegan": False, "allergens": ["gluten", "lactoză"]},
    {"name": "Invitat 35", "cuisine_preference": "asiatică", "vegan": True, "allergens": []},
    {"name": "Invitat 36", "cuisine_preference": "vegană", "vegan": True, "allergens": ["nuci"]},
    {"name": "Invitat 37", "cuisine_preference": "românească", "vegan": False, "allergens": ["gluten"]},
    {"name": "Invitat 38", "cuisine_preference": "italiană", "vegan": True, "allergens": []},
    {"name": "Invitat 39", "cuisine_preference": "asiatică", "vegan": False, "allergens": ["soia"]},
    {"name": "Invitat 40", "cuisine_preference": "vegană", "vegan": True, "allergens": ["lactoză"]},
    {"name": "Invitat 41", "cuisine_preference": "românească", "vegan": False, "allergens": ["ouă"]},
    {"name": "Invitat 42", "cuisine_preference": "italiană", "vegan": True, "allergens": ["gluten", "nuci"]},
    {"name": "Invitat 43", "cuisine_preference": "asiatică", "vegan": False, "allergens": ["pește"]},
    {"name": "Invitat 44", "cuisine_preference": "vegană", "vegan": True, "allergens": []},
    {"name": "Invitat 45", "cuisine_preference": "românească", "vegan": False, "allergens": ["lactoză", "muștar"]},
    {"name": "Invitat 46", "cuisine_preference": "italiană", "vegan": False, "allergens": ["gluten", "ouă"]},
    {"name": "Invitat 47", "cuisine_preference": "asiatică", "vegan": True, "allergens": ["soia"]},
    {"name": "Invitat 48", "cuisine_preference": "vegană", "vegan": True, "allergens": ["nuci"]},
    {"name": "Invitat 49", "cuisine_preference": "românească", "vegan": False, "allergens": ["gluten"]},
    {"name": "Invitat 50", "cuisine_preference": "italiană", "vegan": True, "allergens": ["lactoză"]},
    {"name": "Invitat 51", "cuisine_preference": "universală", "vegan": False, "allergens": ["ouă"]},
    {"name": "Invitat 52", "cuisine_preference": "asiatică", "vegan": True, "allergens": ["soia", "gluten"]},
    {"name": "Invitat 53", "cuisine_preference": "italiană", "vegan": True, "allergens": []},
    {"name": "Invitat 54", "cuisine_preference": "vegană", "vegan": True, "allergens": ["lactoză"]},
    {"name": "Invitat 55", "cuisine_preference": "românească", "vegan": False, "allergens": ["muștar"]},
    {"name": "Invitat 56", "cuisine_preference": "italiană", "vegan": False, "allergens": ["soia"]},
    {"name": "Invitat 57", "cuisine_preference": "asiatică", "vegan": False, "allergens": ["lactoză"]},
    {"name": "Invitat 58", "cuisine_preference": "vegană", "vegan": True, "allergens": ["nuci"]},
    {"name": "Invitat 59", "cuisine_preference": "românească", "vegan": True, "allergens": []},
    {"name": "Invitat 60", "cuisine_preference": "italiană", "vegan": False, "allergens": ["lactoză", "nuci"]},
    {"name": "Invitat 61", "cuisine_preference": "vegană", "vegan": True, "allergens": ["gluten", "soia"]},
    {"name": "Invitat 62", "cuisine_preference": "românească", "vegan": False, "allergens": ["gluten", "ouă"]},
    {"name": "Invitat 63", "cuisine_preference": "asiatică", "vegan": True, "allergens": []},
    {"name": "Invitat 64", "cuisine_preference": "italiană", "vegan": True, "allergens": ["soia"]},
    {"name": "Invitat 65", "cuisine_preference": "universală", "vegan": False, "allergens": ["pește"]},
    {"name": "Invitat 66", "cuisine_preference": "asiatică", "vegan": False, "allergens": ["ouă", "soia"]},
    {"name": "Invitat 67", "cuisine_preference": "vegană", "vegan": True, "allergens": ["gluten"]},
    {"name": "Invitat 68", "cuisine_preference": "românească", "vegan": False, "allergens": ["nuci", "ouă"]},
    {"name": "Invitat 69", "cuisine_preference": "italiană", "vegan": False, "allergens": ["muștar"]},
    {"name": "Invitat 70", "cuisine_preference": "vegană", "vegan": True, "allergens": ["soia", "lactoză"]},
    {"name": "Invitat 71", "cuisine_preference": "românească", "vegan": False, "allergens": []},
    {"name": "Invitat 72", "cuisine_preference": "asiatică", "vegan": True, "allergens": ["gluten", "pește"]},
    {"name": "Invitat 73", "cuisine_preference": "italiană", "vegan": False, "allergens": ["lactoză"]},
    {"name": "Invitat 74", "cuisine_preference": "vegană", "vegan": True, "allergens": ["nuci", "soia"]},
    {"name": "Invitat 75", "cuisine_preference": "românească", "vegan": False, "allergens": ["gluten", "lactoză"]},
    {"name": "Invitat 76", "cuisine_preference": "italiană", "vegan": True, "allergens": []},
    {"name": "Invitat 77", "cuisine_preference": "asiatică", "vegan": False, "allergens": ["gluten"]},
    {"name": "Invitat 78", "cuisine_preference": "vegană", "vegan": True, "allergens": []},
    {"name": "Invitat 79", "cuisine_preference": "românească", "vegan": False, "allergens": ["soia", "lactoză"]},
    {"name": "Invitat 80", "cuisine_preference": "italiană", "vegan": False, "allergens": ["gluten", "ouă"]},
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
