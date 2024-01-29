from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine

db = SQLAlchemy()

def create_app():
	app = Flask(__name__)
	app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:p@ssword@localhost/degreeplannerdb'
	app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

	db.init_app(app)

	@app.route('/')
	def home():
		return 'Hello, World!'

	return app

def check_db_credentials():
    try:
        engine = create_engine('postgresql://postgres:p%40ssword@localhost/degreeplannerdb')
        connection = engine.connect()
        print("Database connection successful")
        connection.close()
    except Exception as e:
        print("Database connection failed. Error : ", str(e))

check_db_credentials()