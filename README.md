🚀 Smart Event Management Platform

A comprehensive full-stack web solution for managing events, automating reservations, and enhancing guest experience through AI integration.






📖 Overview

This project addresses the complexity of modern event organization. Beyond standard CRUD operations for events and users, the platform distinguishes itself by integrating Machine Learning models to solve real-world logistical problems: reducing queue times via facial recognition and improving user engagement through personalized event recommendations.

Key features include:

Secure Authentication: User registration and role-based access control.

AI Smart Check-In: Facial recognition module to automate guest access (Biometric entry).

Organizer Dashboard: Dedicated portal for event creators to manage logistics and attendees.

Recommendation Engine: Suggests events based on user preferences.

👥 The Team (Credits)

This project was designed and developed as a collaborative Bachelor's Thesis by a team of three students from the Technical University of Cluj-Napoca (UTCN).

Contributor	Role & Responsibility
Mihalca Alex	Organizer Module Lead: Full-Stack development for the Organizer actor (Backend & Frontend), Database Design, and Event Management Dashboard.
Petric Darius	System Architect: Core Backend logic, User Authentication, and AI module integration.
Holczli Andrei	Guest Experience: Frontend implementation for Guests and System Testing.

This repository represents a collaborative effort using Git version control and Agile methodologies.

🛠️ Tech Stack
Component	Technology	Description
Backend	Python & Django	Core logic, ORM, flows for organizers and guests.
Frontend	HTML5, CSS3, JavaScript	Responsive dashboard for organizers.
Database	SQLite / PostgreSQL	Relational schema (ER Diagram implementation).
AI / ML	face_recognition, LightFM	Biometric processing + recommendation system.
🌟 Feature Spotlight: Organizer Module

Developed by Alex Mihalca

🔧 Key Capabilities
1. Event Management Dashboard

Responsive UI (HTML, CSS, JavaScript)

Visual feedback for CRUD operations

Real-time event statistics

2. Database Architecture

Designed relational schema (One-to-Many between Organizers → Events)

Optimized database queries

3. Backend Logic (Django)

Custom views/forms for event validation

Permissions ensuring organizers modify only their own resources

⚙️ Installation & Setup
Prerequisites

Python 3.8+

Git installed

1. Clone the repository
git clone https://github.com/alexmhc10/Sistem-Inteligent-de-Gestionare-a-Evenimentelor.git
cd Sistem-Inteligent-de-Gestionare-a-Evenimentelor

2. Local Setup (Windows)
Create & activate a virtual environment:
python -m venv .env
.env\Scripts\activate

Install dependencies:
pip install -r requirements.txt


Set required environment variables (e.g., SECRET_KEY, DATABASE_URL) inside a .env file.

3. Database & Migrations
python manage.py makemigrations
python manage.py migrate


If using PostgreSQL, configure DATABASES inside
sistem_inteligent_de_gestionare_a_evenimentelor/settings.py
or set DATABASE_URL in .env.

4. Required Services (Redis & Celery)

This project uses Redis for:

Celery background tasks

Real-time communication (via Channels)

Redis:

Windows: Use WSL (Linux subsystem) or an external Redis container

Linux / WSL:

sudo service redis-server start

Celery Worker:

Run in a separate terminal:

celery -A sistem_inteligent_de_gestionare_a_evenimentelor worker --loglevel=info --pool=solo


Main optimization task:
base.tasks.run_optimization_task

5. Start the Server
python manage.py runserver 0.0.0.0:8000


Access the app at:
http://127.0.0.1:8000

6. Testing & Linting
Run tests:
python manage.py test

Linting (optional):
pip install flake8
flake8 .

7. Useful Files Overview
File	Purpose
manage.py	Django command utility
requirements.txt	Project dependencies
settings.py	Main configuration file
base/views.py	Core business logic
base/tasks.py	Celery async tasks
algoritmi/meniu.py	Custom algorithm modules
scripts/write.py	Utility scripts
Instructiuni Pentru Rulare Si Utilizare.txt	Localized documentation
8. Contributing

Fork the repository

Create a feature branch

Submit a Pull Request

Please open an Issue before adding major features.

9. License

This project is open-source. See the LICENSE file (e.g., MIT License).

📬 Contact

Alex Mihalca – Full-Stack Developer (Organizer Module)
📧 alexmhc258@gmail.com

Developed as a Bachelor's Thesis at
Faculty of Computer Science – UTCN, Baia Mare
