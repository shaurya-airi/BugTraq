
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_debugtoolbar import DebugToolbarExtension
from config import Config
from elasticsearch import Elasticsearch
app = Flask(__name__)
app.debug = True

app.config.from_object(Config)
app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']]) \
        if app.config['ELASTICSEARCH_URL'] else None
db = SQLAlchemy(app)
# toolbar = DebugToolbarExtension(app)
Bootstrap(app)
from .models import User, Project, Component, BugSearchableMixin
db.create_all()
from app import routes