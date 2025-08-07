# Django Polls Application

A modern, minimalistic web application for creating and managing polls built with Django. This application provides a clean, professional interface for poll creation, voting, and results visualization.

## Features

- **Poll Management**: Create, edit, and delete polls with multiple choice options
- **Dynamic Voting**: Interactive voting interface with real-time feedback
- **Results Visualization**: Clean results display with vote counts and statistics
- **Responsive Design**: Mobile-friendly interface that works across all devices
- **Admin Interface**: Django admin integration for backend management
- **Professional UI**: Minimalistic, clean design following modern web standards

## Technology Stack

- **Backend**: Django 3.2
- **Database**: SQLite (development), easily configurable for PostgreSQL/MySQL
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Python Version**: 3.8+

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Virtual environment (recommended)

### Setup Instructions

1. **Clone the repository**
git clone https://github.com/Anoshpshroff/Django-polls.git
cd django-polls

2. **Create and activate virtual environment**
python3 -m venv venv source venv/bin/activate  # On macOS/Linux
or
venv\Scripts\activate  # On Windows

3. **Install dependencies**
pip install django

4. **Run database migrations**
python manage.py migrate

5. **Create a superuser (optional)**
python manage.py createsuperuser

6. **Start the development server**
python manage.py runserver


7. **Access the application**
- Main application: http://127.0.0.1:8000/polls/
- Admin interface: http://127.0.0.1:8000/admin/

## Project Structure
myproject/
├── manage.py
├── db.sqlite3
├── myproject/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── polls/
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── migrations/
    ├── models.py
    ├── templates/
    │   └── polls/
    │       ├── index.html
    │       ├── detail.html
    │       ├── results.html
    │       ├── create_poll.html
    │       └── edit_polls.html
    ├── tests.py
    ├── urls.py
    └── views.py

## Database Models

### Question Model
- `question_text`: CharField (max 200 characters)
- `pub_date`: DateTimeField for publication date

### Choice Model
- `question`: ForeignKey to Question
- `choice_text`: CharField (max 200 characters)
- `votes`: IntegerField with default value 0

## API Endpoints

**GET /polls/**
- View: IndexView
- Description: Display all available polls

**GET /polls/<question_id>/**
- View: detail
- Description: Show voting interface for specific poll

**GET /polls/<question_id>/results/**
- View: results
- Description: Display poll results

**POST /polls/<question_id>/vote/**
- View: vote
- Description: Process vote submission

**GET/POST /polls/addpoll/**
- View: create_poll
- Description: Create new poll interface

**GET/POST /polls/editpoll/**
- View: edit_polls
- Description: Poll management interface

**GET/POST /admin/**
- View: admin
- Description: Django admin interface



