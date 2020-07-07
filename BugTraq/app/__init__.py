
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
from .models import User, Project, Component
db.create_all()
from app import routes