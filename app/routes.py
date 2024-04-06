from flask import flash, get_flashed_messages, redirect, render_template, request, send_from_directory, url_for, request, jsonify
from flask_login import current_user, login_user
from . import create_app
from .forms import LoginForm, SignupForm
from .user import User, load_user
from .models import hash_password
from app import db, text
from flask import Flask, request, jsonify
from .models import Course, Department, Faculty, User, Major, Minor

app = create_app()

@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('plan'))
    else:
        return render_template('landing.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        try:
            # Fetch user data from the database
            with db.connect() as connection:
                result = connection.execute(text("SELECT * FROM users WHERE email = :identifier OR username = :identifier"), {"identifier": form.identifier.data})
                user_data = result.fetchone()._asdict()

            if user_data is None:
                flash('Login failed. Please try again.', 'danger')
                return render_template('login_form.html', form=form)

            # Create a User object
            user = User(username=user_data['username'], email=user_data['email'], password=user_data['password'])

            # Log the user in
            login_user(user)

            flash('Login successful!', 'success')
            return render_template('login_form.html', form=form)
        except Exception as e:
            flash('Login failed. Please try again.', 'danger')
    return render_template('login_form.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        # validation passed, you can register the user
        hashed_password = hash_password(form.password.data)
        try:
            with db.connect() as connection:
                trans = connection.begin()  # Start a transaction
                result = connection.execute(text("INSERT INTO users (email, username, password) VALUES (:email, :username, :password)"),
                                {"email": form.email.data, "username": form.username.data, "password": hashed_password})
                trans.commit()  # Commit the transaction
            flash('Registration successful!', 'success')
            return render_template('signup_form.html', form=form)
        except Exception as e:
            flash('Registration failed. Error: {}'.format(e), 'danger')
    return render_template('signup_form.html', form=form)

@app.route('/plan')
def plan():
    return render_template('plan.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/search')
def search():
    return render_template('search.html')

from sqlalchemy import or_, func

@app.route('/search_results', methods=['POST'])
@app.route('/search_results', methods=['POST'])
def search_results():
    search_query = request.json.get('query', '')
    filter_option = request.json.get('filter', '')

    # Define a list of models to search in, and the attribute to search for each one
    models = {
        'department': (Department, 'name'),
        'faculty': (Faculty, 'name'),
        'user': (User, 'username'),
        'major': (Major, 'name'),
        'minor': (Minor, 'name'),
        'course': (Course, 'course_code', 'title')
    }

    # Prepare the results
    results = {}

    # If filter_option is not provided or is not valid, search all models
    if filter_option not in models:
        for filter_option, model_info in models.items():
            if filter_option == 'course':
                model, attribute_name1, attribute_name2 = model_info
                items = model.query.filter(or_(getattr(model, attribute_name1).ilike(f'%{search_query}%'), getattr(model, attribute_name2).ilike(f'%{search_query}%'))).all()
                results[filter_option] = [f"{getattr(item, attribute_name1)} {getattr(item, attribute_name2)}" for item in items]
            else:
                model, attribute_name = model_info
                attribute = getattr(model, attribute_name)
                items = model.query.filter(attribute.ilike(f'%{search_query}%')).all()
                results[filter_option] = [getattr(item, attribute_name) for item in items]
    else:
        if filter_option == 'course':
            model, attribute_name1, attribute_name2 = models[filter_option]
            items = model.query.filter(or_(getattr(model, attribute_name1).ilike(f'%{search_query}%'), getattr(model, attribute_name2).ilike(f'%{search_query}%'))).all()
            results[filter_option] = [f"{getattr(item, attribute_name1)} {getattr(item, attribute_name2)}" for item in items]
        else:
            model, attribute_name = models[filter_option]
            attribute = getattr(model, attribute_name)
            items = model.query.filter(attribute.ilike(f'%{search_query}%')).all()
            results[filter_option] = [getattr(item, attribute_name) for item in items]

    # Return the results as JSON
    return jsonify(results)

@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/logout')
def logout():
    return redirect(url_for('home'))