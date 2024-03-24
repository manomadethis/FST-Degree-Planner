from app import create_app
from flask import render_template
from flask import send_from_directory

app = create_app()

@app.route('/')
def home():
    return send_from_directory('static/landing', 'landing.html')

@app.route('/login')
def login():
    return send_from_directory('static/login', 'login.html')

if __name__ == '__main__':
	app.run(debug=True)

# Path: project/app/__init__.py