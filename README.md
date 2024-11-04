# Sistem-Inteligent-de-Gestionare-a-Evenimentelor
Lucrare Licenta grup

''''

Ca sa porniti server:
1.Activati virtualenv
'env\Scripts\activate'

2.Folositi comanda
'python .\manage.py runserver' si lasati terminalul sa mearga

''''

Fiecare modificare o sa aiba aici o mica descriere care contine ce a fost modificat, unde si de cine

''''

''''

Adaugarile de fisiere vor fi cu commit, cu descriere in commit, pentru a putea fi usor de inteles

''''



Avem modele pentru Reviews, Location si Type, cu Location legat de Type, accesibil in baza de date a admin panelului

Aveti un cont in fisieru "user" cu care sa va logati si va puteti face si voi in terminal unul, folosind 
'py manage.py createsuperuser'


Am adaugat login/logout,requirements to update/delete doar admin poate sterge o locatie, doar ownerul locatiei o poate updata, search bar care functioneaza dupa location owner, description, location name, locatia efectiva a unei locatii(modelele, url urile si view urile sunt complete si functionale)


Adaugare verificare user, adaugare recenzii, stergere recenzii, adminul poate refuza un user, adminul poate sterge o locatie, persoanele logate pot da review uri pe locatie