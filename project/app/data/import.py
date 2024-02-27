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
    # Get the raw connection from the SQLAlchemy engine
    conn = db.engine.raw_connection()

    # Create a cursor object
    cur = conn.cursor()

    # Loop over the rows in the DataFrame
    for _, row in df.iterrows():
        # Construct the INSERT statement
        sql = """INSERT INTO courses (code, title, description, level, credit, semester, pre_requisites, co_requisite, is_elective, department, faculty)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        cur.execute(sql, (row['CODE'], row['TITLE'], row['DESCRIPTION'], row['LEVEL'], row['CREDIT'], row['SEMESTER'], row['PRE-REQUISITES'], row['CO-REQUISITE'], row['IS_ELECTIVE'], row['DEPARTMENT'], row['FACULTY']))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()