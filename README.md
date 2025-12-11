#  Smart Event Management Platform

> A comprehensive full-stack web solution for managing events, automating reservations, and enhancing guest experience through AI integration.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Django](https://img.shields.io/badge/Django-4.0%2B-green)
![Status](https://img.shields.io/badge/Status-Bachelor_Thesis-purple)

##  Overview

This project addresses the complexity of modern event organization. Beyond standard CRUD operations for events and users, the platform distinguishes itself by integrating **Machine Learning** models to solve real-world logistical problems: reducing queue times via facial recognition and improving user engagement through personalized event recommendations.

**Key features include:**
* **Secure Authentication:** User registration and role-based access control.
* **AI Smart Check-In:** Facial recognition module to automate guest access (Biometric entry).
* **Organizer Dashboard:** Dedicated portal for event creators to manage logistics and attendees.
* **Recommendation Engine:** Suggests events based on user preferences.

---

##  The Team (Credits)

This project was designed and developed as a collaborative Bachelor's Thesis by a team of three students from the **Technical University of Cluj-Napoca (UTCN)**.

| Contributor | Role & Responsibility |
| :--- | :--- |
| **Mihalca Alex** | **Organizer Module Lead:** Full-Stack development for the Organizer actor (Backend & Frontend), Database Design for event schemas, and Event Management Dashboard. |
| **Petric Darius** | **System Architect:** Core Backend logic, User Authentication, and AI Module integration. |
| **Holczli Andrei** | **Guest Experience:** Frontend implementation for Guests and System Testing. |

*This repository represents a collaborative effort where we utilized Git for version control and Agile methodologies for project management.*

---

## 🛠️ Tech Stack

The application is built using a robust Monolithic architecture ensuring data consistency.

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Backend** | Python & Django | Core logic, ORM, and Organizer workflows. |
| **Frontend** | HTML5, CSS3, JS | Responsive Dashboard for Event Organizers. |
| **Database** | SQLite / PostgreSQL | Relational data design (ER Diagram implementation). |
| **AI / ML** | `face_recognition`, `LightFM` | Biometric processing and recommendation algorithms. |

---

## ⚙️ Installation & Setup

### Prerequisites
* Python 3.8+ and Git installed.

Markdown

### 1. Clone the repository
```bash
git clone [https://github.com/alexmhc10/Sistem-Inteligent-de-Gestionare-a-Evenimentelor.git](https://github.com/alexmhc10/Sistem-Inteligent-de-Gestionare-a-Evenimentelor.git)
cd Sistem-Inteligent-de-Gestionare-a-Evenimentelor
2. Local Setup (Windows)
Create and activate a virtual environment:

Bash

python -m venv .env
.env\Scripts\activate
Install dependencies:

Bash

pip install -r requirements.txt
Configure environment variables (e.g., SECRET_KEY, DATABASE_URL). You can create a .env file in the root directory.

3. Database & Migrations
Bash

python manage.py makemigrations
python manage.py migrate
If using PostgreSQL, configure DATABASES in sistem_inteligent_de_gestionare_a_evenimentelor/settings.py or use the DATABASE_URL variable in your .env file.

4. Required Services
Redis (Used by Celery/Channels):

Windows: Use WSL (Windows Subsystem for Linux) or an external Redis service.

WSL / Linux: sudo service redis-server start

Celery Worker:

Bash

celery -A sistem_inteligent_de_gestionare_a_evenimentelor worker --loglevel=info --pool=solo
Main optimization task: base.tasks.run_optimization_task

5. Start Server
Bash

python manage.py runserver 0.0.0.0:8000
Access the application at: http://127.0.0.1:8000

6. Testing & Linting
Run tests:

Bash

python manage.py test
Linting (Optional):

Bash

pip install flake8
flake8 .
7. Useful Files in Repo
manage.py

requirements.txt

sistem_inteligent_de_gestionare_a_evenimentelor/settings.py

algoritmi/meniu.py

base/views.py

base/tasks.py

sistem_inteligent_de_gestionare_a_evenimentelor/scripts/write.py

Instructiuni Pentru Rulare Si Utilizare.txt

8. Contributing
Fork → feature branch → PR.

Keep commits small and descriptive.

Open an issue for bugs or feature requests.

9. License
Add the desired license type (e.g., MIT) in the LICENSE file.
