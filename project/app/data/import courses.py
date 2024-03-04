import pandas as pd
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app import create_app, db

app = create_app()

with app.app_context():
    conn = db.engine.raw_connection()

    # Read the Excel file (replace with your path to the file)
    df = pd.read_excel("C:/Users/lambe/OneDrive/Documents/Courses/2023-2024/Semester 2/COMP3901/FST-Degree-Planner/project/app/data/chemistry.xlsx")
    print(df.columns)

    # Save the DataFrame to a pickle file
    df.to_pickle("courses.pkl")

    # Create a cursor object
    cur = conn.cursor()

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
        else:
            print(f"Course {row['CODE']} already exists, skipping.")

    # Commit the changes and close the connection
    conn.commit()
    conn.close()