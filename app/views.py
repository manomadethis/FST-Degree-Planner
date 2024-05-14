from collections import defaultdict
from flask import flash, get_flashed_messages, redirect, render_template, request, send_from_directory, url_for, request, jsonify
from flask_login import current_user, login_required, login_user, logout_user
from . import create_app
from .forms import LoginForm, SignupForm
from .user import User, load_user
from .models import AntirequisiteCourse, CorequisiteCourse, MajorCourseAlternative, MajorDepartmentalRequirement, MajorOptionalAdvancedCourse, MajorOptionalCoreCoursesSet1, MajorOptionalCoreCoursesSet2, MajorOptionalCoreCoursesSet3, MajorRecommendedCourse, MajorRequirementFromOptionalAdvancedCourses, MajorRequirementFromOptionalCoreCoursesSet1, MajorRequirementFromOptionalCoreCoursesSet2, MajorRequirementFromOptionalCoreCoursesSet3, Majors, MajorAdvancedCourse, MajorLevel1Course, MinorCourseAlternative, MinorOptionalAdvancedCourse, MinorRecommendedCourse, MinorRequirementFromOptionalAdvancedCourses, Minors, MinorAdvancedCourse, MinorLevel1Course, PrerequisiteCourse, ProgrammeAdvancedCourse, ProgrammeDepartmentalRequirement, ProgrammeLevel1Course, MinorOptionalCoreCoursesSet1, MinorOptionalCoreCoursesSet2, MinorOptionalCoreCoursesSet3, MinorRequirementFromOptionalCoreCoursesSet1, MinorRequirementFromOptionalCoreCoursesSet2, MinorRequirementFromOptionalCoreCoursesSet3, ProgrammeMandatorySummerCourse, ProgrammeOptionalAdvancedCourse, ProgrammeRecommendedCourse, ProgrammeRequirementFromOptionalAdvancedCourses, Programmes, ProgrammeCourseAlternative, Department, Faculty, Course, ProgrammeOptionalCoreCoursesSet1, ProgrammeOptionalCoreCoursesSet2, ProgrammeOptionalCoreCoursesSet3, ProgrammeRequirementFromOptionalCoreCoursesSet1, ProgrammeRequirementFromOptionalCoreCoursesSet2, ProgrammeRequirementFromOptionalCoreCoursesSet3
from app import db, process_degree_plan, text
from flask import Flask, request, jsonify
from .models import Course, Department, Faculty, User, Majors, Minors, Programmes
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user, logout_user, current_user
from sqlalchemy import or_, not_, func
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

# Initialize the response data structure
data = {
    'year1': {'semester1': [], 'semester2': [], 'semester3': []},
    'year2': {'semester1': [], 'semester2': [], 'semester3': []},
    'year3': {'semester1': [], 'semester2': [], 'semester3': []},
}





def semester_credit_count(year, semester):
    return sum(int(Course.query.filter_by(course_code=course_code).first().credit) for course_code in data[f'year{year}'][f'semester{semester}'])

def validate_major(major_name):
    # Query the Majors table to find the major
    major = Majors.query.filter_by(name=major_name).first()

    # Return the name of the major or None
    return major.name if major else None

@app.route('/validate_major', methods=['POST'])
def validate_major_route():
    # Get the major name from the request data
    major_name = request.json.get('major_name')

    # Validate the major
    major = validate_major(major_name)

    # Return the result as JSON
    return jsonify({'message': 'Major found', 'major': major}), 200

def process_courses(courses):
    for course in courses:
        print(f"\nProcessing course: {course.course}")
        # Query the Course table to find the course
        course_details = Course.query.filter_by(course_code=course.course).first()

        if course_details:
            print(f"Found course details for: {course.course}")
            # Check the level of the course
            level = course_details.level
            print(f"Course level: {level}")

            # Parse semesters correctly
            semesters = parse_semesters(course_details.semester)
            print(f"Semesters: {semesters}")

            from sqlalchemy import or_

            # Get the prerequisites for the course
            prerequisites = PrerequisiteCourse.query.filter_by(course_code=course.course).all()
            prerequisite_codes = [prerequisite.prerequisite_course_code for prerequisite in prerequisites]

            # Get the corequisites for the course
            corequisites = CorequisiteCourse.query.filter(or_(CorequisiteCourse.course_code==course.course, CorequisiteCourse.corequisite_course_code==course.course)).all()
            corequisite_codes = [corequisite.corequisite_course_code for corequisite in corequisites if corequisite.corequisite_course_code != course.course]

            # Check if the course is a corequisite of any other course and add it to the corequisites list
            other_corequisites = CorequisiteCourse.query.filter_by(corequisite_course_code=course.course).all()
            for other_corequisite in other_corequisites:
                if other_corequisite.course_code not in corequisite_codes:
                    corequisite_codes.append(other_corequisite.course_code)

            print(f"Prerequisites: {prerequisite_codes}")
            print(f"Corequisites: {corequisite_codes}")

            # Check if all prerequisites and corequisites are satisfied
            if not prerequisite_codes or any(prerequisite_code in data[f'year{level}'][f'semester{semester}'] for prerequisite_code in prerequisite_codes for semester in semesters):
                print(f"All prerequisites satisfied for: {course.course}")
                # Find the next available semester to add the course
                for semester in semesters:
                    # Check if the course has a corequisite that is already in the table
                    if corequisite_codes and any(corequisite_code in data[f'year{level}'][f'semester{semester}'] for corequisite_code in corequisite_codes):
                        print(f"Adding course: {course.course} to year{level} semester{semester} with its corequisite")
                        data[f'year{level}'][f'semester{semester}'].append(course_details.course_code)
                        break
                    elif course_details.course_code not in data[f'year{level}'][f'semester{semester}'] and not any(prerequisite_code in data[f'year{level}'][f'semester{semester}'] for prerequisite_code in prerequisite_codes):
                        print(f"Adding course: {course.course} to year{level} semester{semester}")
                        data[f'year{level}'][f'semester{semester}'].append(course_details.course_code)
                        break

                # Check if the total credits exceed the limit
                credit_limit_attr = f"semester{semester}_credit_limit"
                semester_credit_count_value = semester_credit_count(level, semester)
                credit_limit_value = getattr(Faculty.query.join(Department, Faculty.name == Department.faculty_name).filter(Department.name == Majors.query.filter_by(department=course_details.department_name).first().department).first(), credit_limit_attr)

                print(f"Semester credit count: {semester_credit_count_value}")
                print(f"Credit limit: {credit_limit_value}")

                if semester_credit_count_value > (credit_limit_value - 3):
                    # Find a course with missing or no prerequisites that is offered in more than one semester
                    for course_code in data[f'year{level}'][f'semester{semester}']:
                        course_details = Course.query.filter_by(course_code=course_code).first()
                        prerequisites = PrerequisiteCourse.query.filter_by(course_code=course_code).all()
                        corequisites = CorequisiteCourse.query.filter(or_(CorequisiteCourse.course_code==course_code, CorequisiteCourse.corequisite_course_code==course_code)).all()
                        if not prerequisites or any(prerequisite_code in data[f'year{level}'][f'semester{semester}'] for prerequisite_code in [prerequisite.prerequisite_course_code for prerequisite in prerequisites]):
                            # Check if the course has any corequisites
                            if not corequisites:
                                # Move this course to another semester
                                for next_semester in range(semester + 1, 4):
                                    if course_details.course_code not in data[f'year{level}'][f'semester{next_semester}']:
                                        data[f'year{level}'][f'semester{semester}'].remove(course_details.course_code)
                                        data[f'year{level}'][f'semester{next_semester}'].append(course_details.course_code)
                                        print(f"Moving course: {course.course} from year{level} semester{semester} to year{level} semester{next_semester}")
                                        break
                                break
            else:
                # Place the course in the first available semester
                for semester in semesters:
                    if course_details.course_code not in data[f'year{level}'][f'semester{semester}']:
                        print(f"Adding course with missing prerequisites: {course.course} to year{level} semester{semester}")
                        data[f'year{level}'][f'semester{semester}'].append(course_details.course_code)
                        break

    return jsonify(data), 200

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

    return process_courses(level1_courses)

@app.route('/process_major_advanced_courses', methods=['POST'])
def process_major_advanced_courses():
    # Get the major name from the request data
    major_name = request.json.get('major_name')

    # Validate the major
    major = validate_major(major_name)
    if not major:
        return jsonify({'message': f'Major {major_name} not found'}), 404

    # Query the MajorAdvancedCourse table to find the courses for the major
    advanced_courses = MajorAdvancedCourse.query.filter_by(major=major_name).all()

    return process_courses(advanced_courses)

@app.route('/process_major_course_alternatives', methods=['POST'])
def process_major_course_alternatives():
    # Get the major name from the request data
    major_name = request.json.get('major_name')

    # Validate the major
    major = validate_major(major_name)
    if not major:
        return jsonify({'message': f'Major {major_name} not found'}), 404

    # Query the MajorCourseAlternative table to find the courses for the major
    course_alternative = MajorCourseAlternative.query.filter_by(major=major_name).all()

    # Group the alternatives by course
    course_alternatives = defaultdict(list)
    for course in course_alternative:
        course_alternatives[course.course].append(course.alternative)

    # Return the course and its alternatives
    return jsonify(course_alternatives)

@app.route('/process_major_departmental_requirements', methods=['POST'])
def process_major_departmental_requirements():
    # Get the major name from the request data
    major_name = request.json.get('major_name')

    # Validate the major
    major = validate_major(major_name)
    if not major:
        return jsonify({'message': f'Major {major_name} not found'}), 404

    # Get the level from the request data, default to 1 if not provided
    level_str = request.json.get('level', '1')

    # Parse the level string into a list of levels
    levels = parse_level(level_str)

    # Initialize data dictionary
    data = defaultdict(lambda: defaultdict(list))

    # Process each level
    for level in levels:
        # Get the departmental requirements for the major at this level
        departmental_requirements = MajorDepartmentalRequirement.query.filter_by(major=major_name, level=level).first()

        if not departmental_requirements:
            return jsonify({'message': f'No departmental requirements found for major {major_name} at level {level}'}), 404

        # Get all courses from the department at the specified level
        courses = Course.query.filter(
            Course.department_name == departmental_requirements.department,
            Course.level == str(level)
        ).all()

        # Print the courses
        for course in courses:
            print(f"Course Code: {course.course_code}, Department: {course.department_name}, Level: {course.level}")

        # Initialize total credits
        total_credits = 0

        # Add courses to the data dictionary until the credit limit is reached
        for course in courses:
            if total_credits + int(course.credit) > departmental_requirements.credits_required:
                break
            data[f'year{level}']['semester1'].append(course.course_code)
            total_credits += int(course.credit)

    return jsonify(data), 200


@app.route('/major_recommended_courses', methods=['POST'])
def major_recommended_courses():
    # Get the major name from the request data
    major_name = request.json.get('major_name')

    # Validate the major
    major = validate_major(major_name)
    if not major:
        return jsonify({'message': f'Major {major_name} not found'}), 404

    # Fetch the recommended courses for the major
    recommended_courses = MajorRecommendedCourse.query.filter_by(major=major_name).all()

    # Initialize data dictionary
    data = {
        'year1': {'semester1': [], 'semester2': [], 'semester3': []},
        'year2': {'semester1': [], 'semester2': [], 'semester3': []},
        'year3': {'semester1': [], 'semester2': [], 'semester3': []},
    }

    # Add the recommended courses to the data dictionary
    for course in recommended_courses:
        # Fetch the course from the courses table
        course_info = Course.query.filter_by(course_code=course.course).first()

        # Parse the semesters
        semesters = parse_semesters(course_info.semester)

        # Determine the year based on the level of the course
        year = 'year' + str(course_info.level)

        # Add the course to each semester
        for i in semesters:
            semester = 'semester' + str((i-1)%3 + 1)
            data[year][semester].append(course.course)

    return jsonify(data), 200

@app.route('/major_optional_advanced_courses', methods=['POST'])
def major_optional_advanced_courses():
    # Get the major name from the request data
    major_name = request.json.get('major_name')

    # Validate the major
    major = validate_major(major_name)
    if not major:
        return jsonify({'message': f'Major {major_name} not found'}), 404

    # Fetch the optional advanced courses for the major
    optional_advanced_courses = MajorOptionalAdvancedCourse.query.filter_by(major=major_name).all()

    # Fetch the requirement from the MajorRequirementFromOptionalAdvancedCourses table
    requirement = MajorRequirementFromOptionalAdvancedCourses.query.filter_by(major=major_name).first()

    # Initialize data dictionary
    data = defaultdict(lambda: defaultdict(list))

    # Initialize total credits
    total_credits = 0

    data = {
    'year1': {'semester1': [], 'semester2': [], 'semester3': []},
    'year2': {'semester1': [], 'semester2': [], 'semester3': []},
    'year3': {'semester1': [], 'semester2': [], 'semester3': []},
    }


    # Add the optional advanced courses to the data dictionary
    for course in optional_advanced_courses:
        # Fetch the course from the courses table
        course_info = Course.query.filter_by(course_code=course.course).first()

        # Parse the semesters
        semesters = parse_semesters(course_info.semester)

        # Determine the year based on the level of the course
        year = 'year' + str(course_info.level)

        # Add the course to each semester
        for i in semesters:
            semester = 'semester' + str((i-1)%3 + 1)

            # If number of courses required is not empty, use it to limit the number of courses
            if requirement.number_of_courses_required and len(data[year][semester]) >= requirement.number_of_courses_required:
                break

            # If credits required is not empty, use it to limit the total credits
            if requirement.credits_required and total_credits + int(course_info.credit) > requirement.credits_required:
                break

            data[year][semester].append(course.course)
            total_credits += int(course_info.credit)

    return jsonify(data), 200

def process_optional_core_courses(major_name, set_number):
    # Get the optional core courses for the major from the specified set
    optional_core_courses = getattr(globals()[f"MajorOptionalCoreCoursesSet{set_number}"], 'query').filter_by(major=major_name).all()

    # Fetch the requirement from the corresponding MajorRequirementFromOptionalCoreCoursesSet table
    requirement = getattr(globals()[f"MajorRequirementFromOptionalCoreCoursesSet{set_number}"], 'query').filter_by(major=major_name).first()

    # Initialize data dictionary
    data = {
        'year1': {'semester1': [], 'semester2': [], 'semester3': []},
        'year2': {'semester1': [], 'semester2': [], 'semester3': []},
        'year3': {'semester1': [], 'semester2': [], 'semester3': []},
    }

    # Initialize total credits
    total_credits = 0

    # Add the optional core courses to the data dictionary
    for course in optional_core_courses:
        # Fetch the course from the courses table
        course_info = Course.query.filter_by(course_code=course.course).first()

        # Parse the semesters
        semesters = parse_semesters(course_info.semester)

        # Determine the year based on the level of the course
        year = 'year' + str(course_info.level)

        # Add the course to each semester
        for i in semesters:
            semester = 'semester' + str((i-1)%3 + 1)

            # If number of courses required is not empty, use it to limit the number of courses
            if requirement.number_of_courses_required and len(data[year][semester]) >= requirement.number_of_courses_required:
                break

            # If credits required is not empty, use it to limit the total credits
            if requirement.credits_required and total_credits + int(course_info.credit) > requirement.credits_required:
                break

            data[year][semester].append(course.course)
            total_credits += int(course_info.credit)

    return data

@app.route('/major_optional_core_courses_set_1', methods=['POST'])
def major_optional_core_courses_set_1():
    # Get the major name from the request data
    major_name = request.json.get('major_name')

    # Validate the major
    major = validate_major(major_name)
    if not major:
        return jsonify({'message': f'Major {major_name} not found'}), 404

    data = process_optional_core_courses(major_name, 1)

    return jsonify(data), 200

@app.route('/major_optional_core_courses_set_2', methods=['POST'])
def major_optional_core_courses_set_2():
    # Get the major name from the request data
    major_name = request.json.get('major_name')

    # Validate the major
    major = validate_major(major_name)
    if not major:
        return jsonify({'message': f'Major {major_name} not found'}), 404

    data = process_optional_core_courses(major_name, 2)

    return jsonify(data), 200

@app.route('/major_optional_core_courses_set_3', methods=['POST'])
def major_optional_core_courses_set_3():
    # Get the major name from the request data
    major_name = request.json.get('major_name')

    # Validate the major
    major = validate_major(major_name)
    if not major:
        return jsonify({'message': f'Major {major_name} not found'}), 404

    data = process_optional_core_courses(major_name, 3)

    return jsonify(data), 200

@app.route('/process_major', methods=['POST'])
def process_major():
    # Get the major name from the request data
    major_name = request.json.get('major_name')

    # Validate the major
    major = validate_major(major_name)
    if not major:
        return jsonify({'message': f'Major {major_name} not found'}), 404

    # Process the major level 1 courses
    process_major_level1_courses()

    # Process the major advanced courses
    process_major_advanced_courses()

    # Process the major course alternatives
    process_major_course_alternatives()

    # Process the major departmental requirements
    process_major_departmental_requirements()

    # Process the major recommended courses
    major_recommended_courses()

    # Process the major optional advanced courses
    major_optional_advanced_courses()

    # Process the major optional core courses
    major_optional_core_courses_set_1()
    major_optional_core_courses_set_2()
    major_optional_core_courses_set_3()

    return jsonify(data), 200




def validate_minor(minor_name):
    # Query the Minors table to find the minor
    minor = Minors.query.filter_by(name=minor_name).first()

    # Return the name of the minor or None
    return minor.name if minor else None

@app.route('/validate_minor', methods=['POST'])
def validate_minor_route():
    # Get the minor name from the request data
    minor_name = request.json.get('minor_name')

    # Validate the minor
    minor = validate_minor(minor_name)

    # Return the result as JSON
    return jsonify({'message': 'Minor found', 'minor': minor}), 200

@app.route('/process_minor_level1_courses', methods=['POST'])
def process_minor_level1_courses():
    # Get the minor name from the request data
    minor_name = request.json.get('minor_name')

    # Validate the minor
    minor = validate_minor(minor_name)
    if not minor:
        return jsonify({'message': f'Minor {minor_name} not found'}), 404

    # Query the MinorLevel1Course table to find the courses for the minor
    level1_courses = MinorLevel1Course.query.filter_by(minor=minor_name).all()

    return process_courses(level1_courses)

@app.route('/process_minor_advanced_courses', methods=['POST'])
def process_minor_advanced_courses():
    # Get the minor name from the request data
    minor_name = request.json.get('minor_name')

    # Validate the minor
    minor = validate_minor(minor_name)
    if not minor:
        return jsonify({'message': f'Minor {minor_name} not found'}), 404

    # Query the MinorAdvancedCourse table to find the courses for the minor
    advanced_courses = MinorAdvancedCourse.query.filter_by(minor=minor_name).all()

    return process_courses(advanced_courses)

@app.route('/process_minor_course_alternatives', methods=['POST'])
def process_minor_course_alternatives():
    # Get the minor name from the request data
    minor_name = request.json.get('minor_name')

    # Validate the minor
    minor = validate_minor(minor_name)
    if not minor:
        return jsonify({'message': f'Minor {minor_name} not found'}), 404

    # Query the MinorCourseAlternative table to find the courses for the minor
    course_alternative = MinorCourseAlternative.query.filter_by(minor=minor_name).all()

    # Group the alternatives by course
    course_alternatives = defaultdict(list)
    for course in course_alternative:
        course_alternatives[course.course].append(course.alternative)

    # Return the course and its alternatives
    return jsonify(course_alternatives)

@app.route('/minor_recommended_courses', methods=['POST'])
def minor_recommended_courses():
    # Get the minor name from the request data
    minor_name = request.json.get('minor_name')

    # Validate the minor
    minor = validate_minor(minor_name)
    if not minor:
        return jsonify({'message': f'Minor {minor_name} not found'}), 404

    # Fetch the recommended courses for the minor
    recommended_courses = MinorRecommendedCourse.query.filter_by(minor=minor_name).all()

    # Initialize data dictionary
    data = {
        'year1': {'semester1': [], 'semester2': [], 'semester3': []},
        'year2': {'semester1': [], 'semester2': [], 'semester3': []},
        'year3': {'semester1': [], 'semester2': [], 'semester3': []},
    }

    # Add the recommended courses to the data dictionary
    for course in recommended_courses:
        # Fetch the course from the courses table
        course_info = Course.query.filter_by(course_code=course.course).first()

        # Parse the semesters
        semesters = parse_semesters(course_info.semester)

        # Determine the year based on the level of the course
        year = 'year' + str(course_info.level)

        # Add the course to each semester
        for i in semesters:
            semester = 'semester' + str((i-1)%3 + 1)
            data[year][semester].append(course.course)

    return jsonify(data), 200

@app.route('/minor_optional_advanced_courses', methods=['POST'])
def minor_optional_advanced_courses():
    # Get the minor name from the request data
    minor_name = request.json.get('minor_name')

    # Validate the minor
    minor = validate_minor(minor_name)
    if not minor:
        return jsonify({'message': f'Minor {minor_name} not found'}), 404

    # Fetch the optional advanced courses for the minor
    optional_advanced_courses = MinorOptionalAdvancedCourse.query.filter_by(minor=minor_name).all()

    # Fetch the requirement from the MinorRequirementFromOptionalAdvancedCourses table
    requirement = MinorRequirementFromOptionalAdvancedCourses.query.filter_by(minor=minor_name).first()

    # Initialize data dictionary
    data = defaultdict(lambda: defaultdict(list))

    # Initialize total credits
    total_credits = 0

    data = {
    'year1': {'semester1': [], 'semester2': [], 'semester3': []},
    'year2': {'semester1': [], 'semester2': [], 'semester3': []},
    'year3': {'semester1': [], 'semester2': [], 'semester3': []},
    }


    # Add the optional advanced courses to the data dictionary
    for course in optional_advanced_courses:
        # Fetch the course from the courses table
        course_info = Course.query.filter_by(course_code=course.course).first()

        # Parse the semesters
        semesters = parse_semesters(course_info.semester)

        # Determine the year based on the level of the course
        year = 'year' + str(course_info.level)

        # Add the course to each semester
        for i in semesters:
            semester = 'semester' + str((i-1)%3 + 1)

            # If number of courses required is not empty, use it to limit the number of courses
            if requirement.number_of_courses_required and len(data[year][semester]) >= requirement.number_of_courses_required:
                break

            # If credits required is not empty, use it to limit the total credits
            if requirement.credits_required and total_credits + int(course_info.credit) > requirement.credits_required:
                break

            data[year][semester].append(course.course)
            total_credits += int(course_info.credit)

    return jsonify(data), 200

def process_minor_optional_core_courses(minor_name, set_number):
    # Get the optional core courses for the minor from the specified set
    optional_core_courses = getattr(globals()[f"MinorOptionalCoreCoursesSet{set_number}"], 'query').filter_by(minor=minor_name).all()

    # Fetch the requirement from the corresponding MinorRequirementFromOptionalCoreCoursesSet table
    requirement = getattr(globals()[f"MinorRequirementFromOptionalCoreCoursesSet{set_number}"], 'query').filter_by(minor=minor_name).first()

    # Initialize data dictionary
    data = {
        'year1': {'semester1': [], 'semester2': [], 'semester3': []},
        'year2': {'semester1': [], 'semester2': [], 'semester3': []},
        'year3': {'semester1': [], 'semester2': [], 'semester3': []},
    }

    # Initialize total credits
    total_credits = 0

    # Add the optional core courses to the data dictionary
    for course in optional_core_courses:
        # Fetch the course from the courses table
        course_info = Course.query.filter_by(course_code=course.course).first()

        # Parse the semesters
        semesters = parse_semesters(course_info.semester)

        # Determine the year based on the level of the course
        year = 'year' + str(course_info.level)

        # Add the course to each semester
        for i in semesters:
            semester = 'semester' + str((i-1)%3 + 1)

            # If number of courses required is not empty, use it to limit the number of courses
            if requirement.number_of_courses_required and len(data[year][semester]) >= requirement.number_of_courses_required:
                break

            # If credits required is not empty, use it to limit the total credits
            if requirement.credits_required and total_credits + int(course_info.credit) > requirement.credits_required:
                break

            data[year][semester].append(course.course)
            total_credits += int(course_info.credit)

    return data

@app.route('/minor_optional_core_courses_set_1', methods=['POST'])
def minor_optional_core_courses_set_1():
    # Get the minor name from the request data
    minor_name = request.json.get('minor_name')

    # Validate the minor
    minor = validate_minor(minor_name)
    if not minor:
        return jsonify({'message': f'Minor {minor_name} not found'}), 404

    data = process_minor_optional_core_courses(minor_name, 1)

    return jsonify(data), 200

@app.route('/minor_optional_core_courses_set_2', methods=['POST'])
def minor_optional_core_courses_set_2():
    # Get the minor name from the request data
    minor_name = request.json.get('minor_name')

    # Validate the minor
    minor = validate_minor(minor_name)
    if not minor:
        return jsonify({'message': f'Minor {minor_name} not found'}), 404

    data = process_minor_optional_core_courses(minor_name, 2)

    return jsonify(data), 200

@app.route('/minor_optional_core_courses_set_3', methods=['POST'])
def minor_optional_core_courses_set_3():
    # Get the minor name from the request data
    minor_name = request.json.get('minor_name')

    # Validate the minor
    minor = validate_minor(minor_name)
    if not minor:
        return jsonify({'message': f'Minor {minor_name} not found'}), 404

    data = process_minor_optional_core_courses(minor_name, 3)

    return jsonify(data), 200

@app.route('/process_minor', methods=['POST'])
def process_minor():
    # Get the minor name from the request data
    minor_name = request.json.get('minor_name')

    # Validate the minor
    minor = validate_minor(minor_name)
    if not minor:
        return jsonify({'message': f'Minor {minor_name} not found'}), 404

    # Process the minor level 1 courses
    process_minor_level1_courses()

    # Process the minor advanced courses
    process_minor_advanced_courses()

    # Process the minor course alternatives
    process_minor_course_alternatives()

    # Process the minor recommended courses
    minor_recommended_courses()

    # Process the minor optional advanced courses
    minor_optional_advanced_courses()

    # Process the minor optional core courses
    minor_optional_core_courses_set_1()
    minor_optional_core_courses_set_2()
    minor_optional_core_courses_set_3()

    return jsonify(data), 200




def validate_programme(programme_name):
    # Query the Programmes table to find the programme
    programme = Programmes.query.filter_by(name=programme_name).first()

    # Return the name of the programme or None
    return programme.name if programme else None

@app.route('/validate_programme', methods=['POST'])
def validate_programme_route():
    # Get the programme name from the request data
    programme_name = request.json.get('programme_name')

    # Validate the programme
    programme = validate_programme(programme_name)

    # Return the result as JSON
    return jsonify({'message': 'Programme found', 'programme': programme}), 200

@app.route('/process_programme_level1_courses', methods=['POST'])
def process_programme_level1_courses():
    # Get the programme name from the request data
    programme_name = request.json.get('programme_name')

    # Validate the programme
    programme = validate_programme(programme_name)
    if not programme:
        return jsonify({'message': f'Programme {programme_name} not found'}), 404

    # Query the ProgrammeLevel1Course table to find the courses for the programme
    level1_courses = ProgrammeLevel1Course.query.filter_by(programme=programme_name).all()

    return process_courses(level1_courses)

@app.route('/process_programme_advanced_courses', methods=['POST'])
def process_programme_advanced_courses():
    # Get the programme name from the request data
    programme_name = request.json.get('programme_name')

    # Validate the programme
    programme = validate_programme(programme_name)
    if not programme:
        return jsonify({'message': f'Programme {programme_name} not found'}), 404

    # Query the ProgrammeAdvancedCourse table to find the courses for the programme
    advanced_courses = ProgrammeAdvancedCourse.query.filter_by(programme=programme_name).all()

    return process_courses(advanced_courses)

@app.route('/process_programme_course_alternatives', methods=['POST'])
def process_programme_course_alternatives():
    # Get the programme name from the request data
    programme_name = request.json.get('programme_name')

    # Validate the programme
    programme = validate_programme(programme_name)
    if not programme:
        return jsonify({'message': f'Programme {programme_name} not found'}), 404

    # Query the ProgrammeCourseAlternative table to find the courses for the programme
    course_alternative = ProgrammeCourseAlternative.query.filter_by(programme=programme_name).all()

    # Group the alternatives by course
    course_alternatives = defaultdict(list)
    for course in course_alternative:
        course_alternatives[course.course].append(course.alternative)

    # Return the course and its alternatives
    return jsonify(course_alternatives)

@app.route('/process_programme_departmental_requirements', methods=['POST'])
def process_programme_departmental_requirements():
    # Get the programme name from the request data
    programme_name = request.json.get('programme_name')

    # Validate the programme
    programme = validate_programme(programme_name)
    if not programme:
        return jsonify({'message': f'Programme {programme_name} not found'}), 404

    # Get the level from the request data, default to 1 if not provided
    level_str = request.json.get('level', '1')

    # Parse the level string into a list of levels
    levels = parse_level(level_str)

    # Initialize data dictionary
    data = defaultdict(lambda: defaultdict(list))

    # Process each level
    for level in levels:
        # Get the departmental requirements for the programme at this level
        departmental_requirements = ProgrammeDepartmentalRequirement.query.filter_by(programme=programme_name, level=level).first()

        if not departmental_requirements:
            return jsonify({'message': f'No departmental requirements found for programme {programme_name} at level {level}'}), 404

        # Get all courses from the department at the specified level
        courses = Course.query.filter(
            Course.department_name == departmental_requirements.department,
            Course.level == str(level)
        ).all()

        # Print the courses
        for course in courses:
            print(f"Course Code: {course.course_code}, Department: {course.department_name}, Level: {course.level}")

        # Initialize total credits
        total_credits = 0

        # Add courses to the data dictionary until the credit limit is reached
        for course in courses:
            if total_credits + int(course.credit) > departmental_requirements.credits_required:
                break
            data[f'year{level}']['semester1'].append(course.course_code)
            total_credits += int(course.credit)

    return jsonify(data), 200

@app.route('/programme_recommended_courses', methods=['POST'])
def programme_recommended_courses():
    # Get the programme name from the request data
    programme_name = request.json.get('programme_name')

    # Validate the programme
    programme = validate_programme(programme_name)
    if not programme:
        return jsonify({'message': f'Programme {programme_name} not found'}), 404

    # Fetch the recommended courses for the programme
    recommended_courses = ProgrammeRecommendedCourse.query.filter_by(programme=programme_name).all()

    # Initialize data dictionary
    data = {
        'year1': {'semester1': [], 'semester2': [], 'semester3': []},
        'year2': {'semester1': [], 'semester2': [], 'semester3': []},
        'year3': {'semester1': [], 'semester2': [], 'semester3': []},
    }

    # Add the recommended courses to the data dictionary
    for course in recommended_courses:
        # Fetch the course from the courses table
        course_info = Course.query.filter_by(course_code=course.course).first()

        # Parse the semesters
        semesters = parse_semesters(course_info.semester)

        # Determine the year based on the level of the course
        year = 'year' + str(course_info.level)

        # Add the course to each semester
        for i in semesters:
            semester = 'semester' + str((i-1)%3 + 1)
            data[year][semester].append(course.course)

    return jsonify(data), 200

@app.route('/programme_mandatory_summer_courses', methods=['POST'])
def programme_mandatory_summer_courses():
    # Get the programme name from the request data
    programme_name = request.json.get('programme_name')

    # Validate the programme
    programme = validate_programme(programme_name)
    if not programme:
        return jsonify({'message': f'Programme {programme_name} not found'}), 404

    # Fetch the mandatory summer courses for the programme
    summer_courses = ProgrammeMandatorySummerCourse.query.filter_by(programme=programme_name).all()

    # Initialize data dictionary
    data = {
        'year1': {'semester1': [], 'semester2': [], 'semester3': []},
        'year2': {'semester1': [], 'semester2': [], 'semester3': []},
        'year3': {'semester1': [], 'semester2': [], 'semester3': []},
    }

    # Add the mandatory summer courses to the data dictionary
    for course in summer_courses:
        # Fetch the course from the courses table
        course_info = Course.query.filter_by(course_code=course.course).first()

        # Parse the semesters
        semesters = parse_semesters(course_info.semester)

        # Determine the year based on the level of the course
        year = 'year' + str(course_info.level)

        # Add the course to each semester
        for i in semesters:
            semester = 'semester' + str((i-1)%3 + 1)
            data[year][semester].append(course.course)

    return jsonify(data), 200

@app.route('/programme_optional_advanced_courses', methods=['POST'])
def programme_optional_advanced_courses():
    # Get the programme name from the request data
    programme_name = request.json.get('programme_name')

    # Validate the programme
    programme = validate_programme(programme_name)
    if not programme:
        return jsonify({'message': f'Programme {programme_name} not found'}), 404

    # Fetch the optional advanced courses for the programme
    optional_advanced_courses = ProgrammeOptionalAdvancedCourse.query.filter_by(programme=programme_name).all()

    # Fetch the requirement from the ProgrammeRequirementFromOptionalAdvancedCourses table
    requirement = ProgrammeRequirementFromOptionalAdvancedCourses.query.filter_by(programme=programme_name).first()

    # Initialize data dictionary
    data = defaultdict(lambda: defaultdict(list))

    # Initialize total credits
    total_credits = 0

    data = {
    'year1': {'semester1': [], 'semester2': [], 'semester3': []},
    'year2': {'semester1': [], 'semester2': [], 'semester3': []},
    'year3': {'semester1': [], 'semester2': [], 'semester3': []},
    }

    # Add the optional advanced courses to the data dictionary
    for course in optional_advanced_courses:
        # Fetch the course from the courses table
        course_info = Course.query.filter_by(course_code=course.course).first()

        # Parse the semesters
        semesters = parse_semesters(course_info.semester)

        # Determine the year based on the level of the course
        year = 'year' + str(course_info.level)

        # Add the course to each semester
        for i in semesters:
            semester = 'semester' + str((i-1)%3 + 1)

            # If number of courses required is not empty, use it to limit the number of courses
            if requirement.number_of_courses_required and len(data[year][semester]) >= requirement.number_of_courses_required:
                break

            # If credits required is not empty, use it to limit the total credits
            if requirement.credits_required and total_credits + int(course_info.credit) > requirement.credits_required:
                break

            data[year][semester].append(course.course)
            total_credits += int(course_info.credit)

    return jsonify(data), 200

def process_programme_optional_core_courses(programme_name, set_number):
    # Get the optional core courses for the programme from the specified set
    optional_core_courses = getattr(globals()[f"ProgrammeOptionalCoreCoursesSet{set_number}"], 'query').filter_by(programme=programme_name).all()

    # Fetch the requirement from the corresponding ProgrammeRequirementFromOptionalCoreCoursesSet table
    requirement = getattr(globals()[f"ProgrammeRequirementFromOptionalCoreCoursesSet{set_number}"], 'query').filter_by(programme=programme_name).first()

    # Initialize data dictionary
    data = {
        'year1': {'semester1': [], 'semester2': [], 'semester3': []},
        'year2': {'semester1': [], 'semester2': [], 'semester3': []},
        'year3': {'semester1': [], 'semester2': [], 'semester3': []},
    }

    # Initialize total credits
    total_credits = 0

    # Add the optional core courses to the data dictionary
    for course in optional_core_courses:
        # Fetch the course from the courses table
        course_info = Course.query.filter_by(course_code=course.course).first()

        # Parse the semesters
        semesters = parse_semesters(course_info.semester)

        # Determine the year based on the level of the course
        year = 'year' + str(course_info.level)

        # Add the course to each semester
        for i in semesters:
            semester = 'semester' + str((i-1)%3 + 1)

            # If number of courses required is not empty, use it to limit the number of courses
            if requirement.number_of_courses_required and len(data[year][semester]) >= requirement.number_of_courses_required:
                break

            # If credits required is not empty, use it to limit the total credits
            if requirement.credits_required and total_credits + int(course_info.credit) > requirement.credits_required:
                break

            data[year][semester].append(course.course)
            total_credits += int(course_info.credit)

    return data

@app.route('/programme_optional_core_courses_set_1', methods=['POST'])
def programme_optional_core_courses_set_1():
    # Get the programme name from the request data
    programme_name = request.json.get('programme_name')

    # Validate the programme
    programme = validate_programme(programme_name)
    if not programme:
        return jsonify({'message': f'Programme {programme_name} not found'}), 404

    data = process_programme_optional_core_courses(programme_name, 1)

    return jsonify(data), 200

@app.route('/programme_optional_core_courses_set_2', methods=['POST'])
def programme_optional_core_courses_set_2():
    # Get the programme name from the request data
    programme_name = request.json.get('programme_name')

    # Validate the programme
    programme = validate_programme(programme_name)
    if not programme:
        return jsonify({'message': f'Programme {programme_name} not found'}), 404

    data = process_programme_optional_core_courses(programme_name, 2)

    return jsonify(data), 200

@app.route('/programme_optional_core_courses_set_3', methods=['POST'])
def programme_optional_core_courses_set_3():
    # Get the programme name from the request data
    programme_name = request.json.get('programme_name')

    # Validate the programme
    programme = validate_programme(programme_name)
    if not programme:
        return jsonify({'message': f'Programme {programme_name} not found'}), 404

    data = process_programme_optional_core_courses(programme_name, 3)

    return jsonify(data), 200

@app.route('/process_programme', methods=['POST'])
def process_programme():
    # Get the programme name from the request data
    programme_name = request.json.get('programme_name')

    # Validate the programme
    programme = validate_programme(programme_name)
    if not programme:
        return jsonify({'message': f'Programme {programme_name} not found'}), 404

    # Process the programme level 1 courses
    process_programme_level1_courses()

    # Process the programme advanced courses
    process_programme_advanced_courses()

    # Process the programme course alternatives
    process_programme_course_alternatives()

    # Process the programme recommended courses
    programme_recommended_courses()

    # Process the programme optional advanced courses
    programme_optional_advanced_courses()

    # Process the programme optional core courses
    programme_optional_core_courses_set_1()
    programme_optional_core_courses_set_2()
    programme_optional_core_courses_set_3()

    return jsonify(data), 200








@app.route('/process_single_major', methods=['POST'])
def process_single_major():
    major1 = request.form.get('major1')
    process_major(major1)
    return jsonify({'message': 'Processing single major'})

@app.route('/process_two_majors', methods=['POST'])
def process_two_majors():
    major1 = request.form.get('major1')
    major2 = request.form.get('major2')
    process_major(major1)
    process_major(major2)
    return jsonify({'message': 'Processing two majors'})

@app.route('/process_major_and_minor', methods=['POST'])
def process_major_and_minor():
    major1 = request.form.get('major1')
    minor1 = request.form.get('minor1')
    process_major(major1)
    process_minor(minor1)
    return jsonify({'message': 'Processing major and minor'})

@app.route('/process_major_and_two_minors', methods=['POST'])
def process_major_and_two_minors():
    major1 = request.form.get('major1')
    minor1 = request.form.get('minor1')
    minor2 = request.form.get('minor2')
    process_major(major1)
    process_minor(minor1)
    process_minor(minor2)
    return jsonify({'message': 'Processing major and two minors'})

@app.route('/process_programme', methods=['POST'])
def process_programme():
    programme = request.form.get('programme')
    process_programme(programme)
    return jsonify({'message': 'Processing programme'})

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

def parse_level(level_str):
    levels = []
    level_str = level_str.lower().replace('and', ',').replace('or', ',').replace('&', ',')
    for part in level_str.split(','):
        part = part.strip()
        if 'to' in part:
            start, end = part.split('to')
            levels.extend(list(range(int(start), int(end)+1)))
        else:
            levels.append(int(part))
    return levels


@login_required
@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))