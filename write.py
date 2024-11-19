import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistem_inteligent_de_gestionare_a_evenimentelor.settings')
import django
django.setup()
from base.models import Menu, Guests
import random 
guests = [
    {"firstname": "Ana", "lastname": "Popescu", "email": "ana.popescu@example.com", "age": 25, "cuisine_preference": "Italian", "vegan": False, "allergens": ["gluten", "dairy"]},
    {"firstname": "Ion", "lastname": "Ionescu", "email": "ion.ionescu@example.com", "age": 30, "cuisine_preference": "Mexican", "vegan": True, "allergens": []},
    {"firstname": "Maria", "lastname": "Vasile", "email": "maria.vasile@example.com", "age": 22, "cuisine_preference": "Italian", "vegan": False, "allergens": ["nuts"]},
    {"firstname": "George", "lastname": "Popa", "email": "george.popa@example.com", "age": 35, "cuisine_preference": "Indian", "vegan": True, "allergens": []},
    {"firstname": "Elena", "lastname": "Georgescu", "email": "elena.georgescu@example.com", "age": 28, "cuisine_preference": "Asian", "vegan": False, "allergens": ["soy"]},
    {"firstname": "Mihai", "lastname": "Dumitru", "email": "mihai.dumitru@example.com", "age": 40, "cuisine_preference": "French", "vegan": False, "allergens": ["gluten"]},
    {"firstname": "Ioana", "lastname": "Tudor", "email": "ioana.tudor@example.com", "age": 32, "cuisine_preference": "Mexican", "vegan": True, "allergens": []},
    {"firstname": "Andrei", "lastname": "Munteanu", "email": "andrei.munteanu@example.com", "age": 45, "cuisine_preference": "Italian", "vegan": False, "allergens": ["dairy"]},
    {"firstname": "Gabriela", "lastname": "Stan", "email": "gabriela.stan@example.com", "age": 27, "cuisine_preference": "Indian", "vegan": False, "allergens": ["peanuts"]},
    {"firstname": "Radu", "lastname": "Popescu", "email": "radu.popescu@example.com", "age": 38, "cuisine_preference": "Italian", "vegan": True, "allergens": []},
    {"firstname": "Camelia", "lastname": "Popa", "email": "camelia.popa@example.com", "age": 26, "cuisine_preference": "Chinese", "vegan": False, "allergens": ["soy"]},
    {"firstname": "Cristian", "lastname": "Marin", "email": "cristian.marin@example.com", "age": 29, "cuisine_preference": "Japanese", "vegan": False, "allergens": ["gluten", "fish"]},
    {"firstname": "Laura", "lastname": "Nicolescu", "email": "laura.nicolescu@example.com", "age": 33, "cuisine_preference": "French", "vegan": True, "allergens": []},
    {"firstname": "Florin", "lastname": "Petrescu", "email": "florin.petrescu@example.com", "age": 31, "cuisine_preference": "Mexican", "vegan": False, "allergens": ["corn"]},
    {"firstname": "Violeta", "lastname": "Bălan", "email": "violeta.balan@example.com", "age": 23, "cuisine_preference": "Italian", "vegan": True, "allergens": []},
    {"firstname": "Valentin", "lastname": "Ciobanu", "email": "valentin.ciobanu@example.com", "age": 50, "cuisine_preference": "Indian", "vegan": False, "allergens": ["dairy"]},
    {"firstname": "Adriana", "lastname": "Florea", "email": "adriana.florea@example.com", "age": 39, "cuisine_preference": "Chinese", "vegan": False, "allergens": ["peanuts"]},
    {"firstname": "Stefan", "lastname": "Ionescu", "email": "stefan.ionescu@example.com", "age": 34, "cuisine_preference": "Mexican", "vegan": True, "allergens": []},
    {"firstname": "Sofia", "lastname": "Dima", "email": "sofia.dima@example.com", "age": 28, "cuisine_preference": "Italian", "vegan": False, "allergens": ["gluten"]},
    {"firstname": "Lucian", "lastname": "Petru", "email": "lucian.petru@example.com", "age": 41, "cuisine_preference": "French", "vegan": False, "allergens": ["soy"]},
    {"firstname": "Denisa", "lastname": "Popescu", "email": "denisa.popescu@example.com", "age": 24, "cuisine_preference": "Indian", "vegan": True, "allergens": []},
    {"firstname": "Vlad", "lastname": "Bucur", "email": "vlad.bucur@example.com", "age": 37, "cuisine_preference": "Mexican", "vegan": False, "allergens": ["nuts"]},
    {"firstname": "Alina", "lastname": "Mitrofan", "email": "alina.mitrofan@example.com", "age": 26, "cuisine_preference": "Chinese", "vegan": True, "allergens": []},
    {"firstname": "Lavinia", "lastname": "Cornea", "email": "lavinia.cornea@example.com", "age": 29, "cuisine_preference": "Italian", "vegan": False, "allergens": ["dairy"]},
    {"firstname": "Paul", "lastname": "Mihail", "email": "paul.mihail@example.com", "age": 33, "cuisine_preference": "French", "vegan": False, "allergens": ["gluten"]},
    {"firstname": "Madalina", "lastname": "Iordache", "email": "madalina.iordache@example.com", "age": 40, "cuisine_preference": "Mexican", "vegan": True, "allergens": []},
    {"firstname": "Alexandru", "lastname": "Gheorghe", "email": "alexandru.gheorghe@example.com", "age": 22, "cuisine_preference": "Italian", "vegan": False, "allergens": ["gluten"]},
    {"firstname": "Diana", "lastname": "Tudor", "email": "diana.tudor@example.com", "age": 35, "cuisine_preference": "Chinese", "vegan": False, "allergens": []},
    {"firstname": "Daniel", "lastname": "Negru", "email": "daniel.negru@example.com", "age": 38, "cuisine_preference": "Indian", "vegan": True, "allergens": []},
    {"firstname": "Gabriela", "lastname": "Dumitru", "email": "gabriela.dumitru@example.com", "age": 28, "cuisine_preference": "Mexican", "vegan": False, "allergens": ["corn"]},
    {"firstname": "Cătălina", "lastname": "Popa", "email": "catalina.popa@example.com", "age": 25, "cuisine_preference": "Italian", "vegan": True, "allergens": []},
    {"firstname": "Mihai", "lastname": "Munteanu", "email": "mihai.munteanu@example.com", "age": 30, "cuisine_preference": "Mexican", "vegan": False, "allergens": ["soy"]},
    {"firstname": "Irina", "lastname": "Sârbu", "email": "irina.sarbu@example.com", "age": 26, "cuisine_preference": "Italian", "vegan": True, "allergens": []},
    {"firstname": "Roxana", "lastname": "Constantinescu", "email": "roxana.constantinescu@example.com", "age": 40, "cuisine_preference": "Indian", "vegan": False, "allergens": ["dairy"]}
]

import random

gen = ["masculin", "feminin"]
for guest in guests:
    gender = random.choice(gen)
    
    if gender == "masculin":
        picture = "poze_invitati/male.png"
    else:
        picture = "poze_invitati/female.png"
    
    Guests.objects.create(
        firstname=guest["firstname"],
        lastname=guest["lastname"],
        lastname=guest["email"],
        age=guest["age"],
        gender=gender,
        picture=picture,
        cuisine_preference=guest["cuisine_preference"],
        allergens=",".join(guest['allergens']),
        vegan=guest['vegan'],
    )

