import pandas as pd
import json
from datetime import datetime

FACULTY = "Çorlu Mühendislik Fakültesi"
ACADEMIC_YEAR = "2023-2024"
TERM = "Bahar"
EXAM_TYPE = "Vize"

DAY = "Gündüz"
NIGHT = "Gece"
DAY_AND_NIGHT = "Gündüz ve Gece"

COMP_DEP = "Bilgisayar Mühendisliği"
MAC_DEP  = "Makine Mühendisliği"

COMP_CSV_FILE = "computer.csv"
MAC_CSV_FILE  = "machine.csv"

COMP_JSON_FILE = "computer.json"
MAC_JSON_FILE  = "machine.json"

DEPARTMENT = MAC_DEP

if DEPARTMENT == COMP_DEP:
    CSV_PATH = COMP_CSV_FILE
    JSON_PATH = COMP_JSON_FILE

if DEPARTMENT == MAC_DEP:
    CSV_PATH = MAC_CSV_FILE
    JSON_PATH = MAC_JSON_FILE

# Load the CSV data
csv_file_path = CSV_PATH  # Replace with the actual path to your CSV file
csv_data = pd.read_csv(csv_file_path, names=['CourseCode', 'ExamDate', 'ExamTime', 'Classroom', 'Proctor'])

# Helper functions
def parse_datetime(date_str, time_str):
    return datetime.strptime(f"{date_str} {time_str}", "%d.%m.%Y %H:%M")

def extract_date_components(datetime_obj):
    converted_datetime = pd.to_datetime(datetime_obj).to_pydatetime()
    return {
        "ExamDay": converted_datetime.day,
        "ExamMonth": converted_datetime.month,
        "ExamYear": converted_datetime.year,
        "ExamHour": converted_datetime.hour,
        "ExamMinute": converted_datetime.minute
    }

# Process the CSV data
grouped = csv_data.groupby('CourseCode')
exam_infos = []

for course_code, group in grouped:
    group['DateTime'] = group.apply(lambda row: parse_datetime(row['ExamDate'], row['ExamTime']), axis=1)
    group = group.sort_values(by='DateTime')

    if group['DateTime'].nunique() == 1:
        datetime_components = extract_date_components(group.iloc[0]['DateTime'])
        exam_time = datetime_components['ExamHour'] * 100 + datetime_components['ExamMinute']
        education_type = "Gece" if exam_time >= 1730 else "Gündüz ve Gece"
        exam_info = {
            "Faculty": FACULTY,
            "Department": DEPARTMENT,
            "EducationType": education_type,
            "Year": ACADEMIC_YEAR,
            "Term": TERM,
            "Classrooms": group['Classroom'].tolist(),
            "Proctors": group['Proctor'].tolist(),
            "CourseCode": course_code,
            "ExamType": EXAM_TYPE,
            **datetime_components
        }
        exam_infos.append(exam_info)
    else:
        unique_times = group['DateTime'].unique()
        for i, time_point in enumerate(unique_times):
            sub_group = group[group['DateTime'] == time_point]
            datetime_components = extract_date_components(time_point)
            education_type = "Gündüz" if i == 0 else "Gece"
            exam_info = {
                "Faculty": FACULTY,
                "Department": DEPARTMENT,
                "EducationType": education_type,
                "Year": ACADEMIC_YEAR,
                "Term": TERM,
                "Classrooms": sub_group['Classroom'].tolist(),
                "Proctors": sub_group['Proctor'].tolist(),
                "CourseCode": course_code,
                "ExamType": EXAM_TYPE,
                **datetime_components
            }
            exam_infos.append(exam_info)

# Compile and save the final JSON structure
final_json = {"ExamInfos": exam_infos}
json_output_path = JSON_PATH  # Adjust path as necessary
with open(json_output_path, 'w') as json_file:
    json.dump(final_json, json_file, indent=4, ensure_ascii=False)
