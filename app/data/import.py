from courses import process_courses
from requisites import process_requisites
from app.data.majors import process_majors
from app.data.minors import process_minors
from app.data.programmes import process_programmes

# List of Excel files
files = [
    "C:/Users/lambe/OneDrive/Documents/Courses/2023-2024/Semester 2/COMP3901/FST-Degree-Planner/app/data/departments/chemistry.xlsx",
    "C:/Users/lambe/OneDrive/Documents/Courses/2023-2024/Semester 2/COMP3901/FST-Degree-Planner/app/data/departments/biochemistry.xlsx"
    #"C:/Users/lambe/OneDrive/Documents/Courses/2023-2024/Semester 2/COMP3901/FST-Degree-Planner/app/data/departments/computing.xlsx",
    #"C:/Users/lambe/OneDrive/Documents/Courses/2023-2024/Semester 2/COMP3901/FST-Degree-Planner/app/data/departments/geography and geology.xlsx",
    #"C:/Users/lambe/OneDrive/Documents/Courses/2023-2024/Semester 2/COMP3901/FST-Degree-Planner/app/data/departments/life sciences.xlsx",
    #"C:/Users/lambe/OneDrive/Documents/Courses/2023-2024/Semester 2/COMP3901/FST-Degree-Planner/app/data/departments/mathematics.xlsx",
    #"C:/Users/lambe/OneDrive/Documents/Courses/2023-2024/Semester 2/COMP3901/FST-Degree-Planner/app/data/departments/physics.xlsx",
]

# Loop over the files
for file in files:
    #process_courses(file)
    #process_requisites(file)
    process_majors(file)
    #process_minors(file)
    #process_programmes(file)
