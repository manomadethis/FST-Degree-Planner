from werkzeug.security import generate_password_hash
from . import db

# Testing the database connection
def check_db_credentials():
    try:
        connection = db.engine.connect()
        print("Database connection successful")
        connection.close()
    except Exception as e:
        print("Database connection failed. Error : ", str(e))

def hash_password(password):
    return generate_password_hash(password)

class Course(db.Model):
    __tablename__ = 'courses'
    course_code = db.Column(db.String, primary_key=True)
    title = db.Column(db.String)
    description = db.Column(db.Text)
    level = db.Column(db.Integer)
    credit = db.Column(db.Integer)
    semester = db.Column(db.Integer)
    is_elective = db.Column(db.Boolean)
    department_name = db.Column(db.String, db.ForeignKey('departments.name'))
    faculty_name = db.Column(db.String, db.ForeignKey('faculty.name'))

class Department(db.Model):
    __tablename__ = 'departments'
    name = db.Column(db.String, primary_key=True)
    faculty_name = db.Column(db.String, db.ForeignKey('faculty.name'))

class Faculty(db.Model):
    __tablename__ = 'faculty'
    name = db.Column(db.String, primary_key=True)

class User(db.Model):
    __tablename__ = 'users'
    username = db.Column(db.String, primary_key=True)
    email = db.Column(db.String)
    password = db.Column(db.String)

class Grade(db.Model):
    __tablename__ = 'grades'
    username = db.Column(db.String, db.ForeignKey('users.username'), primary_key=True)
    course_code = db.Column(db.String, db.ForeignKey('courses.course_code'), primary_key=True)
    grade = db.Column(db.Integer)

class Major(db.Model):
    __tablename__ = 'majors'
    name = db.Column(db.String, primary_key=True)
    course_code = db.Column(db.String, db.ForeignKey('courses.course_code'))

class Minor(db.Model):
    __tablename__ = 'minors'
    name = db.Column(db.String, primary_key=True)
    course_code = db.Column(db.String, db.ForeignKey('courses.course_code'))

class PrerequisiteCourse(db.Model):
    __tablename__ = 'prerequisite_courses'
    course_code = db.Column(db.String, db.ForeignKey('courses.course_code'), primary_key=True)
    prerequisite_course_code = db.Column(db.String, primary_key=True)

class PrerequisiteCondition(db.Model):
    __tablename__ = 'prerequisite_conditions'
    course_code = db.Column(db.String, db.ForeignKey('courses.course_code'), primary_key=True)
    condition = db.Column(db.String, primary_key=True)

class CorequisiteCourse(db.Model):
    __tablename__ = 'corequisite_courses'
    course_code = db.Column(db.String, db.ForeignKey('courses.course_code'), primary_key=True)
    corequisite_course_code = db.Column(db.String, primary_key=True)

class CorequisiteCondition(db.Model):
    __tablename__ = 'corequisite_conditions'
    course_code = db.Column(db.String, db.ForeignKey('courses.course_code'), primary_key=True)
    condition = db.Column(db.String, primary_key=True)

class AntirequisiteCourse(db.Model):
    __tablename__ = 'antirequisite_courses'
    course_code = db.Column(db.String, db.ForeignKey('courses.course_code'), primary_key=True)
    antirequisite_course_code = db.Column(db.String, primary_key=True)