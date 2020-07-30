
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_debugtoolbar import DebugToolbarExtension
from config import Config
app = Flask(__name__)
app.debug = True

app.config.from_object(Config)
db = SQLAlchemy(app)
toolbar = DebugToolbarExtension(app)
Bootstrap(app)
from .models import User, Project, Component
db.create_all()
from app import routes