from flask import flash, get_flashed_messages, redirect, render_template, request, send_from_directory, url_for, request, jsonify
from flask_login import current_user, login_required, login_user, logout_user
from . import create_app
from .forms import LoginForm, SignupForm
from .user import User, load_user
from .models import MajorAdvancedCourse, MajorDepartmentalRequirement, MajorLevel1Course, MinorAdvancedCourse, MinorDepartmentalRequirement, MinorLevel1Course, ProgrammeAdvancedCourse, ProgrammeDepartmentalRequirement, ProgrammeLevel1Course, hash_password
from app import db, text
from flask import Flask, request, jsonify
from .models import Course, Department, Faculty, User, Majors, Minors, Programmes
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user, logout_user

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

            if user_data is None or not check_password_hash(user_data['password'], form.password.data):
                flash('Login failed. Please try again.', 'danger')
                return render_template('login_form.html', form=form)

            # Create a User object
            user = User(username=user_data['username'], email=user_data['email'], password=None)

            # Log the user in
            login_user(user)

            # Check if the user is authenticated right after logging them in
            if current_user.is_authenticated:
                flash('Login successful!', 'success')
                return redirect(url_for('plan'))
            else:
                return render_template('login_form.html', form=form)
        except Exception as e:
            flash('Login failed. Please try again.', 'danger')
            return render_template('login_form.html', form=form)
    return render_template('login_form.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        # validation passed, you can register the user
        hashed_password = generate_password_hash(form.password.data)
        try:
            with db.connect() as connection:
                trans = connection.begin()  # Start a transaction
                result = connection.execute(text("INSERT INTO users (email, username, password) VALUES (:email, :username, :password)"),
                                {"email": form.email.data, "username": form.username.data, "password": hashed_password})
                trans.commit()  # Commit the transaction

            # Create a User object
            user = User(username=form.username.data, email=form.email.data, password=hashed_password)

            # Log the user in
            login_user(user)

            flash('Registration successful!', 'success')
            return redirect(url_for('plan'))  # Redirect to the plan page
        except Exception as e:
            flash('Registration failed. Error: {}'.format(e), 'danger')
    return render_template('signup_form.html', form=form)

@login_required
@app.route('/plan')
def plan():
    return render_template('plan.html')

@login_required
@app.route('/profile')
def profile():
    return render_template('profile.html')

@login_required
@app.route('/search')
def search():
    return render_template('search.html')

from sqlalchemy import or_, func

@login_required
@app.route('/search_results', methods=['POST'])
def search_results():
    search_query = request.json.get('query', '')
    filter_option = request.json.get('filter', '')

    # Define a list of models to search in, and the attribute to search for each one
    models = {
        'department': (Department, 'name'),
        'faculty': (Faculty, 'name'),
        'major': (Majors, 'name'),
        'minor': (Minors, 'name'),
        'programme': (Programmes, 'name'),
        'course': (Course, 'course_code', 'title')
    }

    # Prepare the results
    results = {}

    # If filter_option is not provided or is not valid, search all models
    if filter_option not in models:
        filter_option = 'all'

    if filter_option == 'all':
        # Search in all models
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
        # Search in the specified model
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

@app.route('/all/<searchQuery>', methods=['GET'])
def search_all(searchQuery):
    # Perform a search in each resource
    course_results = get_course(searchQuery)
    major_results = get_major(searchQuery)
    minor_results = get_minor(searchQuery)
    programme_results = get_programme(searchQuery)
    faculty_results = get_faculty(searchQuery)
    department_results = get_department(searchQuery)

    # Combine the results
    results = {
        'course': course_results,
        'major': major_results,
        'minor': minor_results,
        'programme': programme_results,
        'faculty': faculty_results,
        'department': department_results
    }

    # Return the results as JSON
    return jsonify(results)

@app.route('/course/<course_code>', methods=['GET'])
def get_course(course_code):
    course = Course.query.get(course_code)
    if course is None:
        return jsonify({'error': 'Course not found'}), 404
    return jsonify({
        'course_code': course.course_code,
        'title': course.title,
        'description': course.description,
        'level': course.level,
        'credit': course.credit,
        'semester': course.semester,
        'is_elective': course.is_elective,
        'department_name': course.department_name,
        'faculty_name': course.faculty_name
    })

@app.route('/major/<name>', methods=['GET'])
def get_major(name):
    major = Majors.query.get(name)
    if major is None:
        return {'error': 'Major not found'}, 404

    level1_credits = major.level1_credits
    advanced_credits = major.advanced_credits
    major_level1_courses = MajorLevel1Course.query.filter_by(major=name).all()
    major_advanced_courses = MajorAdvancedCourse.query.filter_by(major=name).all()
    department = major.department

    return jsonify({
        'name': major.name,
        'level1_credits': level1_credits,
        'advanced_credits': advanced_credits,
        'level1_courses': [course.course for course in major_level1_courses],
        'advanced_courses': [course.course for course in major_advanced_courses],
        'department': department
    })

@app.route('/minor/<name>', methods=['GET'])
def get_minor(name):
    minor = Minors.query.get(name)
    if minor is None:
        return {'error': 'Minor not found'}, 404

    level1_credits = minor.level1_credits
    advanced_credits = minor.advanced_credits
    minor_level1_courses = MinorLevel1Course.query.filter_by(minor=name).all()
    minor_advanced_courses = MinorAdvancedCourse.query.filter_by(minor=name).all()
    department = minor.department

    return jsonify({
        'name': minor.name,
        'level1_credits': level1_credits,
        'advanced_credits': advanced_credits,
        'level1_courses': [course.course for course in minor_level1_courses],
        'advanced_courses': [course.course for course in minor_advanced_courses],
        'department': department
    })

@app.route('/programme/<name>', methods=['GET'])
def get_programme(name):
    programme = Programmes.query.get(name)
    if programme is None:
        return {'error': 'Programme not found'}, 404

    level1_credits = programme.level1_credits
    advanced_credits = programme.advanced_credits
    programme_level1_courses = ProgrammeLevel1Course.query.filter_by(programme=name).all()
    programme_advanced_courses = ProgrammeAdvancedCourse.query.filter_by(programme=name).all()
    deparment = programme.department

    return jsonify({
        'name': programme.name,
        'level1_credits': level1_credits,
        'advanced_credits': advanced_credits,
        'level1_courses': [course.course for course in programme_level1_courses],
        'advanced_courses': [course.course for course in programme_advanced_courses],
        'department': deparment
    })

@app.route('/faculty/<name>', methods=['GET'])
def get_faculty(name):
    faculty = Faculty.query.get(name)
    if faculty is None:
        return {'error': 'Faculty not found'}, 404

    return jsonify({
        'name': faculty.name,
        'level_1_credits_required': faculty.level_1_credits_required,
        'advanced_credits_required': faculty.advanced_credits_required,
        'foundation_credits_required': faculty.foundation_credits_required,
        'departments': [department.name for department in Department.query.filter_by(faculty_name=faculty.name)],
        'notes': faculty.notes
    })

@app.route('/department/<name>', methods=['GET'])
def get_department(name):
    department = Department.query.get(name)
    if department is None:
        return {'error': 'Department not found'}, 404

    majors = [major.name for major in Majors.query.filter_by(department=department.name)]
    minors = [minor.name for minor in Minors.query.filter_by(department=department.name)]
    programmes = [programme.name for programme in Programmes.query.filter_by(department=department.name)]

    return jsonify({
        'name': department.name,
        'faculty_name': department.faculty_name,
        'course_count': Course.query.filter_by(department_name=department.name).count(),
        'majors': majors,
        'minors': minors,
        'programmes': programmes,
    })

@login_required
@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))