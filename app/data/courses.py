import pandas as pd
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app import create_app, db

def process_courses(file_path):
    file_name = os.path.basename(file_path)
    print(f"Updating courses from file: {file_name}")

    app = create_app()

    with app.app_context():
        conn = db.engine.raw_connection()

        # Read the Excel file
        df = pd.read_excel(file_path)
        print(df.columns)

        # Save the DataFrame to a pickle file
        df.to_pickle("courses.pkl")

        # Create a cursor object
        cur = conn.cursor()

        # Initialize counters for inserted and updated courses
        inserted_courses = 0
        updated_courses = 0

        # Loop over the rows in the DataFrame
        for _, row in df.iterrows():
            # Check if the course already exists
            sql = """SELECT 1 FROM courses WHERE course_code = %s"""
            cur.execute(sql, (row['CODE'],))
            if cur.fetchone() is None:
                # If the course does not exist, insert it
                sql = """INSERT INTO courses (course_code, title, description, level, credit, semester, is_elective, department_name, faculty_name)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                cur.execute(sql, (row['CODE'], row['TITLE'], row['DESCRIPTION'], row['LEVEL'], row['CREDIT'], row['SEMESTER'], row['IS_ELECTIVE'], row['DEPARTMENT'], row['FACULTY']))
                inserted_courses += 1
            else:
                # If the course already exists, update it
                sql = """UPDATE courses SET title = %s, description = %s, level = %s, credit = %s, semester = %s, is_elective = %s, department_name = %s, faculty_name = %s
                WHERE course_code = %s"""
                cur.execute(sql, (row['TITLE'], row['DESCRIPTION'], row['LEVEL'], row['CREDIT'], row['SEMESTER'], row['IS_ELECTIVE'], row['DEPARTMENT'], row['FACULTY'], row['CODE']))
                updated_courses += 1

        # Commit the changes and close the connection
        conn.commit()
        conn.close()

        print(f"Inserted {inserted_courses} courses and updated {updated_courses} courses in file {file_name}.")