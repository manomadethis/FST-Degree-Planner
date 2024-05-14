from werkzeug.security import generate_password_hash
from . import db
from sqlalchemy.orm import relationship

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
    level_1_credits_required = db.Column(db.Integer)
    advanced_credits_required = db.Column(db.Integer)
    foundation_credits_required = db.Column(db.Integer)
    semester1_credit_limit = db.Column(db.Integer)
    semester2_credit_limit = db.Column(db.Integer)
    semester3_credit_limit = db.Column(db.Integer)
    notes = db.Column(db.Text)

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




class Majors(db.Model):
    __tablename__ = 'majors'
    name = db.Column(db.String, primary_key=True)
    level1_credits = db.Column(db.Integer, nullable=False)
    advanced_credits = db.Column(db.Integer, nullable=False)
    department = db.Column(db.String, db.ForeignKey('departments.name'), nullable=False)
    notes = db.Column(db.Text)

class MajorLevel1Course(db.Model):
    __tablename__ = 'major_level1_courses'
    major = db.Column(db.String, db.ForeignKey('majors.name'), primary_key=True)
    course = db.Column(db.String, db.ForeignKey('courses.course_code'), primary_key=True)

class MajorAdvancedCourse(db.Model):
    __tablename__ = 'major_advanced_courses'
    major = db.Column(db.String, db.ForeignKey('majors.name'), primary_key=True)
    course = db.Column(db.String, db.ForeignKey('courses.course_code'), primary_key=True)

class MajorCourseAlternative(db.Model):
    __tablename__ = 'major_course_alternatives'
    major = db.Column(db.String, db.ForeignKey('majors.name'), primary_key=True)
    course = db.Column(db.String, db.ForeignKey('courses.course_code'), primary_key=True)
    alternative = db.Column(db.String, db.ForeignKey('courses.course_code'), primary_key=True)

class MajorDepartmentalRequirement(db.Model):
    __tablename__ = 'major_departmental_requirements'
    major = db.Column(db.String, db.ForeignKey('majors.name'), primary_key=True)
    department = db.Column(db.String, db.ForeignKey('departments.name'), primary_key=True)
    credits_required = db.Column(db.Integer, nullable=False)
    level = db.Column(db.Integer)

class MajorRecommendedCourse(db.Model):
    __tablename__ = 'major_recommended_courses'
    major = db.Column(db.String, db.ForeignKey('majors.name'), primary_key=True)
    course = db.Column(db.String, db.ForeignKey('courses.course_code'), primary_key=True)

class MajorOptionalAdvancedCourse(db.Model):
    __tablename__ = 'major_optional_advanced_courses'
    major = db.Column(db.String, db.ForeignKey('majors.name'), primary_key=True)
    course = db.Column(db.String, db.ForeignKey('courses.course_code'), primary_key=True)

class MajorRequirementFromOptionalAdvancedCourses(db.Model):
    __tablename__ = 'major_requirement_from_optional_advanced_courses'
    major = db.Column(db.String, db.ForeignKey('majors.name'), primary_key=True)
    number_of_courses_required = db.Column(db.Integer, nullable=False)
    credits_required = db.Column(db.Integer, nullable=False)

class MajorOptionalCoreCoursesSet1(db.Model):
    __tablename__ = 'major_optional_core_courses_set1'
    major = db.Column(db.String, db.ForeignKey('majors.name'), primary_key=True)
    course = db.Column(db.String, db.ForeignKey('courses.course_code'), primary_key=True)

class MajorRequirementFromOptionalCoreCoursesSet1(db.Model):
    __tablename__ = 'major_requirement_from_optional_core_courses_set1'
    major = db.Column(db.String, db.ForeignKey('majors.name'), primary_key=True)
    number_of_courses_required = db.Column(db.Integer, nullable=False)
    credits_required = db.Column(db.Integer, nullable=False)

class MajorOptionalCoreCoursesSet2(db.Model):
    __tablename__ = 'major_optional_core_courses_set2'
    major = db.Column(db.String, db.ForeignKey('majors.name'), primary_key=True)
    course = db.Column(db.String, db.ForeignKey('courses.course_code'), primary_key=True)

class MajorRequirementFromOptionalCoreCoursesSet2(db.Model):
    __tablename__ = 'major_requirement_from_optional_core_courses_set2'
    major = db.Column(db.String, db.ForeignKey('majors.name'), primary_key=True)
    number_of_courses_required = db.Column(db.Integer, nullable=False)
    credits_required = db.Column(db.Integer, nullable=False)

class MajorOptionalCoreCoursesSet3(db.Model):
    __tablename__ = 'major_optional_core_courses_set3'
    major = db.Column(db.String, db.ForeignKey('majors.name'), primary_key=True)
    course = db.Column(db.String, db.ForeignKey('courses.course_code'), primary_key=True)

class MajorRequirementFromOptionalCoreCoursesSet3(db.Model):
    __tablename__ = 'major_requirement_from_optional_core_courses_set3'
    major = db.Column(db.String, db.ForeignKey('majors.name'), primary_key=True)
    number_of_courses_required = db.Column(db.Integer, nullable=False)
    credits_required = db.Column(db.Integer, nullable=False)





class Minors(db.Model):
    __tablename__ = 'minors'
    name = db.Column(db.String, primary_key=True)
    level1_credits = db.Column(db.Integer, nullable=False)
    advanced_credits = db.Column(db.Integer, nullable=False)
    department = db.Column(db.String, nullable=False)
    notes = db.Column(db.Text)

class MinorLevel1Course(db.Model):
    __tablename__ = 'minor_level1_courses'
    minor = db.Column(db.String, db.ForeignKey('minors.name'), primary_key=True)
    course = db.Column(db.String, primary_key=True)

class MinorAdvancedCourse(db.Model):
    __tablename__ = 'minor_advanced_courses'
    minor = db.Column(db.String, db.ForeignKey('minors.name'), primary_key=True)
    course = db.Column(db.String, primary_key=True)

class MinorCourseAlternative(db.Model):
    __tablename__ = 'minor_course_alternatives'
    minor = db.Column(db.String, db.ForeignKey('minors.name'), primary_key=True)
    course = db.Column(db.String, primary_key=True)
    alternative = db.Column(db.String, primary_key=True)

class MinorDepartmentalRequirement(db.Model):
    __tablename__ = 'minor_departmental_requirements'
    minor = db.Column(db.String, db.ForeignKey('minors.name'), primary_key=True)
    department = db.Column(db.String, primary_key=True)
    credits_required = db.Column(db.Integer, nullable=False)
    level = db.Column(db.Integer)

class MinorRecommendedCourse(db.Model):
    __tablename__ = 'minor_recommended_courses'
    minor = db.Column(db.String, db.ForeignKey('minors.name'), primary_key=True)
    course = db.Column(db.String, primary_key=True)

class MinorOptionalAdvancedCourse(db.Model):
    __tablename__ = 'minor_optional_advanced_courses'
    minor = db.Column(db.String, db.ForeignKey('minors.name'), primary_key=True)
    course = db.Column(db.String, primary_key=True)

class MinorRequirementFromOptionalAdvancedCourses(db.Model):
    __tablename__ = 'minor_requirement_from_optional_advanced_courses'
    minor = db.Column(db.String, db.ForeignKey('minors.name'), primary_key=True)
    number_of_courses_required = db.Column(db.Integer)
    credits_required = db.Column(db.Integer)

class MinorOptionalCoreCoursesSet1(db.Model):
    __tablename__ = 'minor_optional_core_courses_set1'
    minor = db.Column(db.String, db.ForeignKey('minors.name'), primary_key=True)
    course = db.Column(db.String, primary_key=True)

class MinorRequirementFromOptionalCoreCoursesSet1(db.Model):
    __tablename__ = 'minor_requirement_from_optional_core_courses_set1'
    minor = db.Column(db.String, db.ForeignKey('minors.name'), primary_key=True)
    number_of_courses_required = db.Column(db.Integer)
    credits_required = db.Column(db.Integer)

class MinorOptionalCoreCoursesSet2(db.Model):
    __tablename__ = 'minor_optional_core_courses_set2'
    minor = db.Column(db.String, db.ForeignKey('minors.name'), primary_key=True)
    course = db.Column(db.String, primary_key=True)

class MinorRequirementFromOptionalCoreCoursesSet2(db.Model):
    __tablename__ = 'minor_requirement_from_optional_core_courses_set2'
    minor = db.Column(db.String, db.ForeignKey('minors.name'), primary_key=True)
    number_of_courses_required = db.Column(db.Integer)
    credits_required = db.Column(db.Integer)

class MinorOptionalCoreCoursesSet3(db.Model):
    __tablename__ = 'minor_optional_core_courses_set3'
    minor = db.Column(db.String, db.ForeignKey('minors.name'), primary_key=True)
    course = db.Column(db.String, primary_key=True)

class MinorRequirementFromOptionalCoreCoursesSet3(db.Model):
    __tablename__ = 'minor_requirement_from_optional_core_courses_set3'
    minor = db.Column(db.String, db.ForeignKey('minors.name'), primary_key=True)
    number_of_courses_required = db.Column(db.Integer)
    credits_required = db.Column(db.Integer)




class Programmes(db.Model):
    __tablename__ = 'programmes'
    name = db.Column(db.String(50), primary_key=True)
    level1_credits = db.Column(db.Integer, nullable=False)
    advanced_credits = db.Column(db.Integer, nullable=False)
    department = db.Column(db.String(50), nullable=False)
    notes = db.Column(db.Text)

class ProgrammeLevel1Course(db.Model):
    __tablename__ = 'programme_level1_courses'
    programme = db.Column(db.String(50), db.ForeignKey('programmes.name'), primary_key=True)
    course = db.Column(db.String(8), primary_key=True)

class ProgrammeAdvancedCourse(db.Model):
    __tablename__ = 'programme_advanced_courses'
    programme = db.Column(db.String(50), db.ForeignKey('programmes.name'), primary_key=True)
    course = db.Column(db.String(8), primary_key=True)

class ProgrammeCourseAlternative(db.Model):
    __tablename__ = 'programme_course_alternatives'
    programme = db.Column(db.String(50), db.ForeignKey('programmes.name'), primary_key=True)
    course = db.Column(db.String(8), primary_key=True)
    alternative = db.Column(db.String(8), primary_key=True)

class ProgrammeDepartmentalRequirement(db.Model):
    __tablename__ = 'programme_departmental_requirements'
    programme = db.Column(db.String(50), db.ForeignKey('programmes.name'), primary_key=True)
    department = db.Column(db.String(50), primary_key=True)
    credits_required = db.Column(db.Integer, nullable=False)
    level = db.Column(db.Integer)

class ProgrammeMandatorySummerCourse(db.Model):
    __tablename__ = 'programme_mandatory_summer_courses'
    programme = db.Column(db.String(50), db.ForeignKey('programmes.name'), primary_key=True)
    course = db.Column(db.String(8), primary_key=True)

class ProgrammeRecommendedCourse(db.Model):
    __tablename__ = 'programme_recommended_courses'
    programme = db.Column(db.String(50), db.ForeignKey('programmes.name'), primary_key=True)
    course = db.Column(db.String(8), primary_key=True)

class ProgrammeOptionalAdvancedCourse(db.Model):
    __tablename__ = 'programme_optional_advanced_courses'
    programme = db.Column(db.String(50), db.ForeignKey('programmes.name'), primary_key=True)
    course = db.Column(db.String(8), primary_key=True)

class ProgrammeRequirementFromOptionalAdvancedCourses(db.Model):
    __tablename__ = 'programme_requirement_from_optional_advanced_courses'
    programme = db.Column(db.String(50), db.ForeignKey('programmes.name'), primary_key=True)
    number_of_courses_required = db.Column(db.Integer)
    credits_required = db.Column(db.Integer)

class ProgrammeOptionalCoreCoursesSet1(db.Model):
    __tablename__ = 'programme_optional_core_courses_set1'
    programme = db.Column(db.String(50), db.ForeignKey('programmes.name'), primary_key=True)
    course = db.Column(db.String(8), primary_key=True)

class ProgrammeRequirementFromOptionalCoreCoursesSet1(db.Model):
    __tablename__ = 'programme_requirement_from_optional_core_courses_set1'
    programme = db.Column(db.String(50), db.ForeignKey('programmes.name'), primary_key=True)
    number_of_courses_required = db.Column(db.Integer)
    credits_required = db.Column(db.Integer)

class ProgrammeOptionalCoreCoursesSet2(db.Model):
    __tablename__ = 'programme_optional_core_courses_set2'
    programme = db.Column(db.String(50), db.ForeignKey('programmes.name'), primary_key=True)
    course = db.Column(db.String(8), primary_key=True)

class ProgrammeRequirementFromOptionalCoreCoursesSet2(db.Model):
    __tablename__ = 'programme_requirement_from_optional_core_courses_set2'
    programme = db.Column(db.String(50), db.ForeignKey('programmes.name'), primary_key=True)
    number_of_courses_required = db.Column(db.Integer)
    credits_required = db.Column(db.Integer)

class ProgrammeOptionalCoreCoursesSet3(db.Model):
    __tablename__ = 'programme_optional_core_courses_set3'
    programme = db.Column(db.String(50), db.ForeignKey('programmes.name'), primary_key=True)
    course = db.Column(db.String(8), primary_key=True)

class ProgrammeRequirementFromOptionalCoreCoursesSet3(db.Model):
    __tablename__ = 'programme_requirement_from_optional_core_courses_set3'
    programme = db.Column(db.String(50), db.ForeignKey('programmes.name'), primary_key=True)
    number_of_courses_required = db.Column(db.Integer)
    credits_required = db.Column(db.Integer)

