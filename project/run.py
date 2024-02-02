from app import create_app
from flask import render_template
app = create_app()

@app.route('/index/')
def home():
    return render_template('header.html')

if __name__ == '__main__':
	app.run(debug=True)

# Path: project/app/__init__.py