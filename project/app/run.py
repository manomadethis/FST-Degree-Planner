from app import create_app
from flask import render_template
from flask import send_from_directory
from app.login import LoginForm
import os
#from app import app, db, login_manager
from flask import render_template, request, redirect, url_for, flash, session, abort,send_from_directory
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
from app.models import UserProfile
#from app.forms import LoginForm, UploadForm
from werkzeug.security import check_password_hash


app = create_app()

@app.route('/')
def home():
    return send_from_directory('static/landing', 'landing.html')

@app.route('/login')
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = UserProfile.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            
            login_user(user)

            flash('Login successful!', 'success')
            return redirect(url_for('upload'))

        else:
            flash('Invalid username or password. Please try again.', 'danger')

    #return render_template('login.html', form=form)
    return send_from_directory('static/login', 'login.html')

if __name__ == '__main__':
	app.run(debug=True)

# Path: project/app/__init__.py