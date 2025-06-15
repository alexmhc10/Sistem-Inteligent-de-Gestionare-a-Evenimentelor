# 🎊 Formular de Înregistrare pentru Invitați
## GuestSelfRegistrationForm - Colectarea Datelor într-un Mod Prietenos

Acest formular permite invitaților să își completeze propriile date pentru **"Nunta Ana și Florin"** într-un mod natural și plăcut, colectând în fundal toate informațiile necesare algoritmului inteligent de aranjare a meselor.

---

## 🎯 **Filozofia Formularului**

### ❌ **NU Face:**
- Nu expune complexitatea tehnică a algoritmului
- Nu folosește termeni tehnici ("prioritate", "scoring", "algoritm")
- Nu cere informații care par invazive sau ciudate
- Nu pare un interogatoriu

### ✅ **Face:**
- Colectează date critical pentru algoritm într-un mod natural
- Folosește un limbaj conversațional și prietenos
- Explică de ce are nevoie de informații ("pentru confortul tău")
- Pare o conversație obișnuită de RSVP

---

## 📋 **Structura în 7 Pași**

### **🙋‍♀️ PASUL 1: CINE EȘTI?**
```
- Prenumele tău
- Numele tău de familie  
- Vârsta ta → "Ne ajută să aranjăm mesele cu persoane de vârste apropiate"
- Numărul tău de telefon → "Pentru contact în ziua evenimentului"
```

**Mapare algoritm:**
- `first_name`, `last_name` → Identificare unică
- `age` → **CRITIC** pentru algoritm (grupare ±10 ani)
- `phone` → Logistică

---

### **👥 PASUL 2: CUM TE CUNOAȘTEM?**
```
- "Cum îi cunoști pe Ana și Florin?"
  • Sunt din familia miresei
  • Sunt din familia mirelui  
  • Sunt prieten apropiat al miresei/mirelui
  • Suntem prieteni cu amândoi
  • Suntem colegi de serviciu
  • Ne cunoaștem din facultate
  • Suntem vecini
  • Sunt prieten al familiei

- "Cât de apropiați sunteți?"
  • Suntem foarte apropiați (familie, prieteni cei mai buni)
  • Suntem apropiați (prieteni buni)
  • Ne cunoaștem bine (colegi, cunoscuți)
  • Ne cunoaștem mai puțin (prieteni comuni, distant)
```

**Mapare algoritm:**
- **CRITIC** - Determină `TableGroup` și `priority` (1-10)
- Familie → Prioritate 10
- Prieteni apropiați → Prioritate 8
- Colegi → Prioritate 6
- Alții → Prioritate 4-5

---

### **🍽️ PASUL 3: PREFERINȚE MÂNCARE**
```
- "Ce tip de mâncare îți place cel mai mult?"
  • Mâncare românească tradițională
  • Mâncare italiană
  • Mâncare franceză
  • Mâncare mediteraneană
  • Mâncare internațională
  • Bucătărie modernă/fusion
  • Nu am preferințe speciale

- "Urmez o dietă vegană" ☐
- "Sunt vegetarian/ă" ☐
- "Am următoarele alergii alimentare:" [checkbox list]
```

**Mapare algoritm:**
- **FOARTE IMPORTANT** - `cuisine_preference` pentru compatibilitate
- `vegan`, `vegetarian` → Restricții dietetice
- `allergens` → Siguranță și compatibilitate masa

---

### **👨‍👩‍👧‍👦 PASUL 4: CU CINE VENII?**
```
- "Vin însoțit/ă de o persoană (+1)" ☐
- "Numele persoanei care mă însoțește"
- "Câți copii vin cu mine?" (0-5)
```

**Mapare algoritm:**
- **IMPORTANT** - Capacitatea efectivă a mesei
- Copii → Ajustează spațiul necesar

---

### **🧠 PASUL 5: PREFERINȚE SOCIALE**
```
- "Cum ești la evenimente sociale?"
  • Îmi place să cunosc oameni noi și să socializez mult
  • Îmi place să stau de vorbă, dar nu sunt foarte extrovert
  • Prefer conversații mai liniștite în grupuri mici
  • Depinde de oameni și de atmosferă

- "Există persoane cu care ți-ar plăcea să stai la masă?"
  → nume separate prin virgulă (opțional)
```

**Mapare algoritm:**
- `social_personality` → Echilibrarea personalităților
- `preferred_table_companions` → Cerințe specifice

---

### **♿ PASUL 6: CERINȚE SPECIALE**
```
- "Am nevoie de o masă cu acces facil" ☐
- "Vin cu o persoană în vârstă care are nevoie de atenție specială" ☐
- "Cum ajungi de obicei la evenimente?"
  • De obicei ajung puțin mai devreme
  • Ajung întotdeauna la timp  
  • Ajung de obicei cu câteva minute întârziere
```

**Mapare algoritm:**
- `mobility_assistance` → Poziții strategice mese
- `elderly_person_with_me` → Considerații comfort
- `arrival_style` → Organizarea serviri

---

### **📝 PASUL 7: ALTE INFORMAȚII**
```
- "Alte cerințe sau informații importante"
  → Text liber pentru cerințe speciale

- "Alte preferințe sau restricții alimentare"  
  → Text liber pentru restricții suplimentare
```

**Mapare algoritm:**
- `special_requests` → Considerații manuale
- `dietary_notes` → Informații suplimentare meniu

---

## 🔄 **Calculul Automat al Priorității**

### Algoritm Prioritate:
```python
def _calculate_priority(self):
    relationship_priority = {
        'bride_family': 10,      # Familia miresei
        'groom_family': 10,      # Familia mirelui
        'bride_close_friend': 8, # Prieteni apropiați mireasa
        'groom_close_friend': 8, # Prieteni apropiați mirele
        'mutual_friend': 7,      # Prieteni comuni
        'work_colleague': 6,     # Colegi serviciu
        'university_friend': 6,  # Prieteni facultate
        'family_friend': 7,      # Prieteni familie
        'neighbor': 5,           # Vecini
        'other': 4,             # Alții
    }
    
    closeness_modifier = {
        'very_close': +1,    # Foarte apropiați
        'close': 0,          # Apropiați
        'acquaintance': -1,  # Cunoscuți
        'distant': -2,       # Distanți
    }
    
    return base_priority + modifier  # (1-10)
```

### Exemple Prioritate Finală:
- **Familia foarte apropiată**: 10 + 1 = **10** (prioritate maximă)
- **Prieteni apropiați**: 8 + 0 = **8**
- **Colegi cunoscuți**: 6 + (-1) = **5**
- **Vecini distanți**: 5 + (-2) = **3**

---

## 🎨 **Template HTML Recomandat**

### Structură Multi-Step:
```html
<div class="guest-registration-wizard">
    <!-- Progress Bar -->
    <div class="progress mb-4">
        <div class="progress-bar" id="registration-progress"></div>
    </div>
    
    <!-- Step 1: Cine ești? -->
    <div class="step active" id="step-1">
        <h3>🙋‍♀️ Să te cunoaștem!</h3>
        <p class="text-muted">Câteva informații de bază despre tine</p>
        <!-- Fields: first_name, last_name, age, phone -->
    </div>
    
    <!-- Step 2: Cum te cunoaștem? -->
    <div class="step" id="step-2">
        <h3>👥 Povestea voastră</h3>
        <p class="text-muted">Cum îi cunoști pe Ana și Florin?</p>
        <!-- Fields: relationship_to_couple, how_close -->
    </div>
    
    <!-- Step 3: Preferințe mâncare -->
    <div class="step" id="step-3">
        <h3>🍽️ Să te răsfățăm</h3>
        <p class="text-muted">Ce îți place să mănânci?</p>
        <!-- Fields: cuisine_preference, vegan, vegetarian, allergens -->
    </div>
    
    <!-- ... etc pentru toate step-urile -->
</div>
```

### CSS Modern și Prietenos:
```css
.guest-registration-wizard {
    max-width: 600px;
    margin: 0 auto;
    padding: 2rem;
    background: linear-gradient(135deg, #fff, #f8f9fa);
    border-radius: 20px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
}

.step {
    display: none;
    animation: slideIn 0.3s ease-out;
}

.step.active {
    display: block;
}

.form-control, .form-select {
    border-radius: 12px;
    border: 2px solid #e1e8ed;
    padding: 12px 16px;
    transition: all 0.3s ease;
}

.form-control:focus, .form-select:focus {
    border-color: #D4AF37;
    box-shadow: 0 0 0 3px rgba(212, 175, 55, 0.1);
}
```

---

## 🎯 **View și URL Integration**

### View Recomandat:
```python
def guest_self_registration(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    if request.method == 'POST':
        form = GuestSelfRegistrationForm(request.POST, event=event)
        if form.is_valid():
            guest = form.save()
            event.guests.add(guest)
            
            # Mesaj success
            messages.success(request, 
                f"Mulțumim, {guest.profile.first_name}! "
                f"Te-am înregistrat pentru {event.event_name}. "
                f"Îți vom trimite detaliile despre masa ta în curând!"
            )
            
            # Rulează algoritmul în background (opțional)
            # update_table_arrangements.delay(event_id)
            
            return redirect('guest_registration_success', event_id=event.id)
    else:
        form = GuestSelfRegistrationForm(event=event)
    
    return render(request, 'guest_registration.html', {
        'form': form, 
        'event': event
    })
```

### URL Configuration:
```python
urlpatterns = [
    path('events/<int:event_id>/register/', 
         views.guest_self_registration, 
         name='guest_registration'),
    path('events/<int:event_id>/register/success/', 
         views.guest_registration_success, 
         name='guest_registration_success'),
]
```

---

## 📊 **Avantajele vs. Formularul Tehnic**

| Aspect | ComprehensiveGuestForm (Admin) | GuestSelfRegistrationForm (User) |
|--------|--------------------------------|----------------------------------|
| **Audiență** | Organizatori evenimente | Invitați |
| **Limbaj** | Tehnic, algoritmic | Conversațional, prietenos |
| **Scopuri** | Control complet, optimizare | UX plăcut, adoptare înaltă |
| **Complexitate** | 20+ câmpuri tehnice | 15 câmpuri naturale |
| **Prioritate** | Manual (1-10) | Calculată automat |
| **Alergii** | Lista completă | Checkbox-uri simple |
| **Caracteristici sociale** | 10 subiecte conversație | Personalitate generală |
| **Utilizare** | Populare în masă | Self-service individual |

---

## 🎉 **Rezultat Final**

### Pentru Invitați:
- ✅ Experiență plăcută și naturală  
- ✅ Înțeleg de ce sunt întrebați
- ✅ Se simt părtași la organizare
- ✅ Procedură rapidă (5-7 minute)

### Pentru Algoritm:
- ✅ Toate datele critice colectate
- ✅ Prioritatea calculată automat
- ✅ Grupuri sociale create natural
- ✅ Compatibilitate maximă

### Pentru Organizatori:
- ✅ Reducerea muncii manuale
- ✅ Date mai precise și actuale
- ✅ Invitați mai angajați
- ✅ Aranjamente optimizate automat

**🎊 Concluzie**: Un formular care oferă experiența perfectă pentru invitați în timp ce alimentează algoritmul cu datele necesare pentru aranjamente inteligente de mese! 