import pandas as pd
import sys
import os
import re
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app import create_app, db

app = create_app()

def process_requisites():
    with app.app_context():
        conn = db.engine.raw_connection()

        # Read the DataFrame from the pickle file
        df = pd.read_pickle("courses.pkl")
        print(df.columns)

        # Create a cursor object
        cur = conn.cursor()

        # Regular expression pattern for normal requisites
        pattern = re.compile(r'[A-Z]{4}\d{4}')

        for _, row in df.iterrows():

            # Get prerequisites and corequisites strings
            prerequisites_str = row['PRE-REQUISITES'] if 'PRE-REQUISITES' in row and pd.notna(row['PRE-REQUISITES']) else None
            corequisites_str = row['CO-REQUISITE'] if 'CO-REQUISITE' in row and pd.notna(row['CO-REQUISITE']) else None

            # Insert prerequisites and corequisites strings into conditions tables
            if prerequisites_str is not None:
                sql = """SELECT * FROM prerequisite_conditions WHERE course_code = %s AND condition = %s"""
                cur.execute(sql, (row['CODE'], prerequisites_str))
                result = cur.fetchone()
                if result is None:
                    sql = """INSERT INTO prerequisite_conditions (course_code, condition) VALUES (%s, %s)"""
                    cur.execute(sql, (row['CODE'], prerequisites_str))
            if corequisites_str is not None:
                sql = """SELECT * FROM corequisite_conditions WHERE course_code = %s AND condition = %s"""
                cur.execute(sql, (row['CODE'], corequisites_str))
                result = cur.fetchone()
                if result is None:
                    sql = """INSERT INTO corequisite_conditions (course_code, condition) VALUES (%s, %s)"""
                    cur.execute(sql, (row['CODE'], corequisites_str))

            # Split prerequisites and corequisites into individual courses
            prerequisite_courses = pattern.findall(prerequisites_str) if prerequisites_str is not None else []
            corequisite_courses = pattern.findall(corequisites_str) if corequisites_str is not None else []

            # Insert individual courses into courses tables
            for pre in prerequisite_courses:
                sql = """SELECT * FROM prerequisite_courses WHERE course_code = %s AND prerequisite_course_code = %s"""
                cur.execute(sql, (row['CODE'], pre))
                result = cur.fetchone()
                if result is None:
                    sql = """INSERT INTO prerequisite_courses (course_code, prerequisite_course_code) VALUES (%s, %s)"""
                    cur.execute(sql, (row['CODE'], pre))
            for co in corequisite_courses:
                sql = """SELECT * FROM corequisite_courses WHERE course_code = %s AND corequisite_course_code = %s"""
                cur.execute(sql, (row['CODE'], co))
                result = cur.fetchone()
                if result is None:
                    sql = """INSERT INTO corequisite_courses (course_code, corequisite_course_code) VALUES (%s, %s)"""
                    cur.execute(sql, (row['CODE'], co))

            # Get antirequisites string
            antirequisites_str = row['ANTI-REQUISITE'] if 'ANTI-REQUISITE' in row and pd.notna(row['ANTI-REQUISITE']) else None

            # Split antirequisites into individual courses
            antirequisite_courses = pattern.findall(antirequisites_str) if antirequisites_str is not None else []

            # Insert individual courses into antirequisite_courses table
            for anti in antirequisite_courses:
                sql = """SELECT * FROM antirequisite_courses WHERE course_code = %s AND antirequisite_course_code = %s"""
                cur.execute(sql, (row['CODE'], anti))
                result = cur.fetchone()
                if result is None:
                    sql = """INSERT INTO antirequisite_courses (course_code, antirequisite_course_code) VALUES (%s, %s)"""
                    cur.execute(sql, (row['CODE'], anti))
            # Commit the changes and close the connection
    conn.commit()
    conn.close()