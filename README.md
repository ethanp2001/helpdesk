# IT Helpdesk (prototype)
This is a prototype project designed for Level 5 Software Engineering & Agile DTS apprenticeship
## Installation
### Requirements
- flask
- flask_login
- flask_wtf
- wtforms
- dotenv
### (Optional) Make a Python Virtual Environment
``python -m venv /path/to/new/virtual/environment``
- On Windows:
    ``PS C:\> <venv>\Scripts\Activate.ps1``
- On MacOS/Linux:
    ``$ source <venv>/bin/activate``
### Install Dependencies
``pip install -r requirements.txt``
- Create .env file within the /app directory, in which enter "'SECRET_KEY' = 'yoursecretkey'"
### Start the app
From /app directory:
``py main.py``
Navigate to http://localhost:5000 in your browser.