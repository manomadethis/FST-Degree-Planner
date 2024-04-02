import sqlite3
from collections import deque
import spacy
import sqlite3
from collections import deque

def parse_user_input(user_input):
    majors, minors, preferences = user_input.split(',')
    return majors, minors, preferences

def validate_input(majors, minors):
    if len(majors) > 2 or (len(majors) == 1 and len(minors) > 2):
        raise ValueError("Invalid input")

def query_courses(majors, minors, preferences):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute("SELECT * FROM courses WHERE major IN (?) OR minor IN (?) OR preference IN (?)", (majors, minors, preferences))
    courses = c.fetchall()

    conn.close()

    return courses


def check_prerequisites(courses):
    conn = sqlite3.connect('your_database.db')
    cur = conn.cursor()
    prerequisites = {}

    for course in courses:
        cur.execute("SELECT prerequisite_course_code FROM prerequisite_courses WHERE course_code = ?", (course,))
        results = cur.fetchall()
        prerequisites[course] = [result[0] for result in results]

    conn.close()

    return prerequisites


def create_degree_plan(courses, prerequisites):
    degree_plan = []
    course_dependencies = {course: set() for course in courses}
    dependent_courses = {course: [] for course in courses}

    for course in courses:
        for prerequisite in prerequisites[course]:
            course_dependencies[course].add(prerequisite)
            dependent_courses[prerequisite].append(course)

    queue = deque(course for course, dependencies in course_dependencies.items() if not dependencies)

    while queue:
        course = queue.popleft()
        degree_plan.append(course)

        for dependent_course in dependent_courses[course]:
            course_dependencies[dependent_course].remove(course)

            if not course_dependencies[dependent_course]:
                queue.append(dependent_course)

    if any(course_dependencies.values()):
        raise ValueError("Circular dependency detected")

    return degree_plan

def assign_courses(user_input):
    majors, minors, preferences = parse_user_input(user_input)
    validate_input(majors, minors)
    courses = query_courses(majors, minors, preferences)
    courses = check_prerequisites(courses)
    degree_plan = create_degree_plan(courses)
    return degree_plan

def load_nlp_model():
    nlp = spacy.load('en_core_web_sm')
    return nlp

def process_user_request(user_input):
    nlp_model = load_nlp_model()
    doc = nlp_model(user_input)
