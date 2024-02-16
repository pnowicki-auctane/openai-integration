from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
import openai

# Ustawienie podstawowej konfiguracji
app = Flask(__name__)
CORS(app)

# Ładowanie zmiennych środowiskowych
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://slackgptadmin:gpt@localhost/slackgpt'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')

db = SQLAlchemy(app)

# Ustawienie klucza API OpenAI
openai.api_key = app.config['OPENAI_API_KEY']

# Importowanie tras po zainicjowaniu aplikacji Flask i bazy danych
from app import routes
