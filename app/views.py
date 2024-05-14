from flask import flash, get_flashed_messages, redirect, render_template, request, send_from_directory, url_for, request, jsonify
from flask_login import current_user, login_required, login_user, logout_user
from . import create_app
from .forms import LoginForm, SignupForm
from .user import User, load_user
from .models import AntirequisiteCourse, CorequisiteCourse, Majors, MajorAdvancedCourse, MajorLevel1Course, Minors, MinorAdvancedCourse, MinorLevel1Course, PrerequisiteCourse, ProgrammeAdvancedCourse, ProgrammeLevel1Course
from app import db, process_degree_plan, text
from flask import Flask, request, jsonify
from .models import Course, Department, Faculty, User, Majors, Minors, Programmes
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user, logout_user, current_user
from sqlalchemy import or_, func
from sqlalchemy.orm import joinedload
import re

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

@app.route('/create_plan')
def create_plan():
    courses = Course.query.all()
    majors = Majors.query.all()
    minors = Minors.query.all()
    programmes = Programmes.query.all()
    return render_template('create_plan.html', courses=courses, majors=majors, minors=minors, programmes=programmes)

@login_required
@app.route('/profile')
def profile():
    return render_template('profile.html')

@login_required
@app.route('/search')
def search():
    return render_template('search.html')

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

@app.route('/get_courses')
def get_courses():
    courses = Course.query.all()
    return jsonify([f"{course.course_code} - {course.title}" for course in courses])

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

@app.route('/get_majors')
def get_majors():
    majors = Majors.query.all()
    return jsonify([major.name for major in majors])

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

@app.route('/get_minors')
def get_minors():
    minors = Minors.query.all()
    return jsonify([minor.name for minor in minors])

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

@app.route('/get_programmes')
def get_programmes():
    programmes = Programmes.query.all()
    return jsonify([programme.name for programme in programmes])

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

@app.route('/get_departments')
def get_departments():
    departments = Department.query.all()
    return jsonify([department.name for department in departments])

@app.route('/get_faculties')
def get_faculties():
    faculties = Faculty.query.all()
    return jsonify([faculty.name for faculty in faculties])


    


def validate_major(major_name):
    # Query the Majors table to find the major
    major = Majors.query.filter_by(name=major_name).first()

    # Return the name of the major or None
    return major.name if major else None

@app.route('/process_major_level1_courses', methods=['POST'])
def process_major_level1_courses():
    # Get the major name from the request data
    major_name = request.json.get('major_name')

    # Validate the major
    major = validate_major(major_name)
    if not major:
        return jsonify({'message': f'Major {major_name} not found'}), 404

    # Query the MajorLevel1Course table to find the courses for the major
    level1_courses = MajorLevel1Course.query.filter_by(major=major_name).all()

    # Initialize the response data structure
    data = {
        'year1': {'semester1': [], 'semester2': [], 'semester3': []},
        'year2': {'semester1': [], 'semester2': [], 'semester3': []},
        'year3': {'semester1': [], 'semester2': [], 'semester3': []},
    }

    # Process the courses
    for course in level1_courses:
        # Query the Course table to find the course
        course_details = Course.query.filter_by(course_code=course.course).first()

        if course_details:
            # Check the level of the course
            level = course_details.level

            # Parse semesters correctly
            semesters = parse_semesters(course_details.semester)

            # Get the prerequisites, corequisites, and antirequisites for the course
            prerequisites = PrerequisiteCourse.query.filter_by(course_code=course.course).all()
            corequisites = CorequisiteCourse.query.filter_by(course_code=course.course).all()
            antirequisites = AntirequisiteCourse.query.filter_by(course_code=course.course).all()

            # Process the prerequisites
            for prerequisite in prerequisites:
                prerequisite_course = Course.query.filter_by(course_code=prerequisite.prerequisite_course_code).first()
                if prerequisite_course and prerequisite_course.course_code not in data[f'year{level}'][f'semester{semester}']:
                    # Delay processing this course
                    continue

            # Process the corequisites
            for corequisite in corequisites:
                corequisite_course = Course.query.filter_by(course_code=corequisite.corequisite_course_code).first()
                if corequisite_course and corequisite_course.course_code not in data[f'year{level}'][f'semester{semester}']:
                    # Add the corequisite to the same semester
                    data[f'year{level}'][f'semester{semester}'].append(corequisite_course.course_code)

            # Process the antirequisites
            for antirequisite in antirequisites:
                antirequisite_course = Course.query.filter_by(course_code=antirequisite.antirequisite_course_code).first()
                if antirequisite_course and antirequisite_course.course_code in data[f'year{level}'][f'semester{semester}']:
                    # Remove the antirequisite from the semester
                    data[f'year{level}'][f'semester{semester}'].remove(antirequisite_course.course_code)

            # Add the course to the appropriate semesters in the response data
            for semester in semesters:
                data[f'year{level}'][f'semester{semester}'].append(course_details.course_code)

    return jsonify(data), 200

def parse_semesters(semester_str):
    semesters = []
    semester_str = semester_str.lower().replace('and', ',').replace('or', ',').replace('&', ',')
    for part in semester_str.split(','):
        part = part.strip()
        if 'to' in part:
            start, end = part.split('to')
            semesters.extend(list(range(int(start), int(end)+1)))
        else:
            semesters.append(int(part))
    return semesters


@login_required
@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))