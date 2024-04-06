from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from flask_wtf.csrf import CSRFProtect
import os

db = SQLAlchemy()
login_manager = LoginManager()
text = db.text

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:p%40ssword@localhost/degreeplannerdb'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.urandom(24)
    app.config['WTF_CSRF_ENABLED'] = False

    db.init_app(app)
    csrf = CSRFProtect(app)

    login_manager.init_app(app)

    return app

app = create_app()

def check_db_credentials():
    try:
        engine = create_engine('postgresql://postgres:p%40ssword@localhost/degreeplannerdb')
        connection = engine.connect()
        print("Database connection successful")
        connection.close()
    except Exception as e:
        print("Database connection failed. Error : ", str(e))

check_db_credentials()