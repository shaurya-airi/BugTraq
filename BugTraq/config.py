import os


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or \
        b'w\xdeDl\x91C\x1f\xa0\x93\x9f\x92}\x06\x08\xfc\n'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///BugTraq.db'+'?check_same_thread=False'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    ELASTICSEARCH_URL = 'http://localhost:9200'
