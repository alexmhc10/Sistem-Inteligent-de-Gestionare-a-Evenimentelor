# 🚀 Smart Event Management Platform

> A comprehensive full-stack web solution for managing events, automating reservations, and enhancing guest experience through AI integration.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Django](https://img.shields.io/badge/Django-4.0%2B-green)
![Status](https://img.shields.io/badge/Status-Bachelor_Thesis-purple)

## 📖 Overview

This project addresses the complexity of modern event organization. Beyond standard CRUD operations for events and users, the platform distinguishes itself by integrating **Machine Learning** models to solve real-world logistical problems: reducing queue times via facial recognition and improving user engagement through personalized event recommendations.

### **Key features include:**
- **Secure Authentication:** User registration and role-based access control.  
- **AI Smart Check-In:** Facial recognition module to automate guest access (Biometric entry).  
- **Organizer Dashboard:** Dedicated portal for event creators to manage logistics and attendees.  
- **Recommendation Engine:** Suggests events based on user preferences.  

---

## 👥 The Team (Credits)

This project was designed and developed as a collaborative Bachelor's Thesis by a team of three students from the **Technical University of Cluj-Napoca (UTCN)**.

| Contributor | Role & Responsibility |
|------------|-----------------------|
| **Mihalca Alex** | **Organizer Module Lead:** Full-Stack development for the Organizer actor (Backend & Frontend), Database Design, and Event Management Dashboard. |
| **Petric Darius** | **System Architect:** Core Backend logic, User Authentication, and AI module integration. |
| **Holczli Andrei** | **Guest Experience:** Frontend implementation for Guests and System Testing. |

---

## 🛠️ Tech Stack

| Component | Technology | Description |
|----------|------------|-------------|
| **Backend** | Python & Django | Core logic, ORM, flows for organizers and guests. |
| **Frontend** | HTML5, CSS3, JavaScript | Responsive dashboard for organizers. |
| **Database** | SQLite / PostgreSQL | Relational schema (ER Diagram implementation). |
| **AI / ML** | `face_recognition`, `LightFM` | Biometric processing + recommendation system. |

---

## 🌟 Feature Spotlight: Organizer Module  
*Developed by Alex Mihalca*

### 🔧 Key Capabilities
#### **1. Event Management Dashboard**
- Responsive UI (HTML, CSS, JavaScript)
- Visual feedback for CRUD operations  
- Real-time event statistics

#### **2. Database Architecture**
- Designed relational schema (One-to-Many between Organizers → Events)
- Optimized database queries

#### **3. Backend Logic (Django)**
- Custom views/forms for event validation  
- Permissions ensuring organizers modify only their own resources  

---

## ⚙️ Installation & Setup

### **Prerequisites**
- Python **3.8+**
- Git installed

---

### **1. Clone the repository**
```bash
git clone https://github.com/alexmhc10/Sistem-Inteligent-de-Gestionare-a-Evenimentelor.git
cd Sistem-Inteligent-de-Gestionare-a-Evenimentelor
```

---

### **2. Local Setup (Windows)**

#### Create & activate a virtual environment:
```bash
python -m venv .env
.env\Scripts\activate
```

#### Install dependencies:
```bash
pip install -r requirements.txt
```

---

### **3. Database & Migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

---

### **4. Redis & Celery**

```bash
sudo service redis-server start
celery -A sistem_inteligent_de_gestionare_a_evenimentelor worker --loglevel=info --pool=solo
```

---

### **5. Run Server**
```bash
python manage.py runserver 0.0.0.0:8000
```

---

## 📬 Contact
Alex Mihalca — Full-Stack Developer  
📧 alexmhc258@gmail.com
