from courses import process_file
from requisites import process_requisites

# List of Excel files
files = [
    "C:/Users/lambe/OneDrive/Documents/Courses/2023-2024/Semester 2/COMP3901/FST-Degree-Planner/app/data/biochemistry.xlsx",
    "C:/Users/lambe/OneDrive/Documents/Courses/2023-2024/Semester 2/COMP3901/FST-Degree-Planner/app/data/chemistry.xlsx",
    "C:/Users/lambe/OneDrive/Documents/Courses/2023-2024/Semester 2/COMP3901/FST-Degree-Planner/app/data/computing.xlsx",
    "C:/Users/lambe/OneDrive/Documents/Courses/2023-2024/Semester 2/COMP3901/FST-Degree-Planner/app/data/geography and geology.xlsx",
    "C:/Users/lambe/OneDrive/Documents/Courses/2023-2024/Semester 2/COMP3901/FST-Degree-Planner/app/data/life sciences.xlsx",
    "C:/Users/lambe/OneDrive/Documents/Courses/2023-2024/Semester 2/COMP3901/FST-Degree-Planner/app/data/mathematics.xlsx",
    "C:/Users/lambe/OneDrive/Documents/Courses/2023-2024/Semester 2/COMP3901/FST-Degree-Planner/app/data/physics.xlsx",
]

# Loop over the files
for file in files:
    process_file(file)
    process_requisites()