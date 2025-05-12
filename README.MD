# Navy Crew Registration Chatbot

![Navy Chatbot Banner](https://img.shields.io/badge/Django-4.0+-green) ![LangChain](https://img.shields.io/badge/LangChain-0.0.300+-blue) ![License](https://img.shields.io/badge/License-MIT-yellow)

A Django-based web application with an AI-powered chatbot for registering naval crew and ship information. The chatbot leverages **LangChain** and **LangGraph** to process natural language queries, store data in a SQLite database, and provide mission-related insights using the **Grok API** from xAI.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)

---

## Features

- **User Authentication**: Register, log in, and log out securely using Django's authentication system.
- **AI-Powered Chatbot**: Process naval queries (e.g., ship details, mission types) using natural language processing.
- **Data Management**: Store ship, crew, mission, and port information in a SQLite database.
- **Mission Insights**: Analyze mission priority, crew readiness, and strategic advantages using the Grok API.
- **Responsive UI**: Clean, Bootstrap-based interface for seamless user interaction.
- **Logging**: Detailed debug and error logging for development and troubleshooting.

---

## Tech Stack

- **Backend**: Django 4.0+, Python 3.11
- **Frontend**: HTML, CSS (Bootstrap 5), JavaScript (jQuery for AJAX)
- **AI/LLM**: LangChain, LangGraph, Grok API (via `langchain_groq`)
- **Database**: SQLite (default Django backend)
- **Dependencies**:
  - `Django>=4.0`
  - `langchain>=0.0.300`
  - `langchain-community>=0.0.300`
  - `langchain-core>=0.0.300`
  - `langgraph>=0.0.30`
  - `langchain-groq>=0.0.1`

---

## Prerequisites

- **Python 3.11**: Ensure Python is installed. [Download Python](https://www.python.org/downloads/).
- **Virtual Environment**: Recommended for dependency isolation (e.g., `venv`).
- **Grok API Key**: Obtain an API key from [xAI](https://x.ai/api).
- **Git**: For cloning the repository.
- **Web Browser**: Chrome, Firefox, or any modern browser for testing.

---

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/navy-crew-registration-chatbot.git
   cd navy-crew-registration-chatbot
   ```

2. **Create a Virtual Environment**:
   ```bash
   python -m venv .envRegisAgent
   ```

3. **Activate the Virtual Environment**:
   - On Windows:
     ```bash
     .envRegisAgent\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source .envRegisAgent/bin/activate
     ```

4. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Apply Database Migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create a Superuser (Optional)**:
   ```bash
   python manage.py createsuperuser
   ```

---

## Configuration

1. **Set Environment Variables**:
   - Add your Grok API key to the environment:
     - On Windows:
       ```bash
       set GROQ_API_KEY=your-api-key-here
       ```
     - On macOS/Linux:
       ```bash
       export GROQ_API_KEY=your-api-key-here
       ```
   - Alternatively, add it to your virtual environment’s activation script or a `.env` file (requires `python-dotenv`).

2. **Collect Static Files**:
   ```bash
   python manage.py collectstatic
   ```

3. **Verify Settings**:
   - Check `Navy_Crew_Registration_Chatbot/settings.py` for:
     - `STATICFILES_DIRS` pointing to `Navy_registrar/static/`.
     - `LOGGING` configuration for debugging (see below).

---

## Usage

1. **Run the Development Server**:
   ```bash
   python manage.py runserver
   ```

2. **Access the Application**:
   - Open `http://localhost:8000` in your browser.
   - Register a new user or log in with an existing account.
   - Navigate to the chatbot page (`/chatbot/`) to interact with the AI.

3. **Example Query**:
   ```
   I am Captain of Ballistic Missile Submarine Ship INS Arihant going on a deterrence mission with crew size 100 coming from Visakhapatnam. What is the priority of my mission?
   ```
   - The chatbot will process the query, store ship/crew data, and respond with mission priority, crew readiness, and strategic insights.

4. **Admin Interface**:
   - Access `http://localhost:8000/admin/` with superuser credentials to view stored data (ships, crews, missions, ports).

---

## Project Structure

```
navy-crew-registration-chatbot/
├── Navy_Crew_Registration_Chatbot/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
├── Navy_registrar/
│   ├── migrations/
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   ├── js/
│   │   │   └── script.js
│   ├── templates/
│   │   ├── base.html
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── chatbot.html
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   ├── utils.py
│   ├── views.py
├── .envRegisAgent/
├── db.sqlite3
├── manage.py
├── requirements.txt
├── README.md
```

- **Navy_registrar/**: Main Django app containing models, views, templates, and static files.
- **utils.py**: Contains the LangGraph workflow for processing chatbot queries.
- **static/**: CSS and JavaScript for the frontend.
- **templates/**: HTML templates for rendering pages.

---

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature`).
3. Make your changes and commit (`git commit -m "Add your feature"`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Open a Pull Request.

Please ensure your code follows PEP 8 and includes relevant tests.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Acknowledgements

- [xAI](https://x.ai/) for providing the Grok API.
- [Django](https://www.djangoproject.com/) for the robust web framework.
- [LangChain](https://langchain.dev/) and [LangGraph](https://langgraph.dev/) for AI workflow integration.
- [Bootstrap](https://getbootstrap.com/) for responsive UI components.

---

**Happy Sailing with the Navy Crew Registration Chatbot! 🚢**