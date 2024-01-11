import pandas as pd
import json
import locale

# Set the locale to Turkish
locale.setlocale(locale.LC_ALL, 'tr_TR.utf8')


# Load the CSV file
csv_file_path = 'cmf.csv'
csv_data = pd.read_csv(csv_file_path)

# Filter and process the data
filtered_csv_data = csv_data[csv_data['Bölüm'].str.contains('BİLGİSAYAR MÜHENDİSLİĞİ')]
filtered_csv_data['CourseCode'] = filtered_csv_data['Ders Adı:'].str.split().str[0]
filtered_csv_data['ExamDay'] = pd.to_datetime(filtered_csv_data['Sınav Tarihi:']).dt.day
filtered_csv_data['ExamMonth'] = pd.to_datetime(filtered_csv_data['Sınav Tarihi:']).dt.month
filtered_csv_data['ExamYear'] = pd.to_datetime(filtered_csv_data['Sınav Tarihi:']).dt.year
filtered_csv_data['ExamHour'] = pd.to_datetime(filtered_csv_data['Sınav Saati:']).dt.hour
filtered_csv_data['ExamMinute'] = pd.to_datetime(filtered_csv_data['Sınav Saati:']).dt.minute
filtered_csv_data = filtered_csv_data.convert_dtypes()

# Grouping by 'CourseCode'
grouped_by_course = filtered_csv_data.groupby('CourseCode')

# Creating JSON entries
json_entries = []

for course, group in grouped_by_course:
    grouped_by_time = group.groupby(['ExamDay', 'ExamMonth', 'ExamYear', 'ExamHour', 'ExamMinute'])
    for _, time_group in grouped_by_time:
        if len(time_group['Bölüm'].unique()) == 2:
            education_type = 'Gündüz ve Gece'
        else:
            education_type = 'Gündüz' if 'BİLGİSAYAR MÜHENDİSLİĞİ' in time_group['Bölüm'].values else 'Gece'

        classrooms = time_group['Sınıflar'].dropna().astype(str).unique().tolist()

        json_entry = {
            "Faculty": "Çorlu Mühendislik Fakültesi",
            "Department": "Bilgisayar Mühendisliği",
            "EducationType": education_type,
            "Year": "2023-2024",
            "Term": "Güz",
            "Classrooms": classrooms,
            "CourseCode": course,
            "ExamType": "Final",
            "ExamDay": int(time_group['ExamDay'].iloc[0]),
            "ExamMonth": int(time_group['ExamMonth'].iloc[0]),
            "ExamYear": int(time_group['ExamYear'].iloc[0]),
            "ExamHour": int(time_group['ExamHour'].iloc[0]),
            "ExamMinute": int(time_group['ExamMinute'].iloc[0])
        }

        json_entries.append(json_entry)

# Constructing the JSON structure
new_json_data = {"ExamInfos": json_entries}

# Saving the new JSON data to a file
final_corrected_json_file_path = 'bilgisayar.json'
with open(final_corrected_json_file_path, 'w', encoding='utf-8') as file:
    json.dump(new_json_data, file, ensure_ascii=False, indent=4)
