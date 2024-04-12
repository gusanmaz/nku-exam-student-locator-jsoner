from PyPDF2 import PdfMerger
import os
import json
import datetime


def parse_exam_time(day, month, year, hour, minute):
    return datetime.datetime(year, month, day, hour, minute)


def load_json_data(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)


def find_pdfs_for_proctor(base_path, department, course_code, education_type, classroom, exam_datetime):
    folder_name = f"{department}_{course_code}_{education_type}"
    folder_path = os.path.join(base_path, folder_name)
    pdf_files = []
    try:
        for file_name in os.listdir(folder_path):
            if file_name.endswith('.pdf') and classroom in file_name:
                pdf_file_path = os.path.join(folder_path, file_name)
                pdf_files.append((pdf_file_path, exam_datetime))
    except FileNotFoundError:
        print(f"Directory not found: {folder_path}")
    return pdf_files


def merge_pdfs(output_path, proctor_name, pdf_files):
    if not pdf_files:
        print(f"No PDF files found for {proctor_name}. Nothing to merge.")
        return

    # Sort by the associated exam datetime
    pdf_files.sort(key=lambda x: x[1])
    merger = PdfMerger()
    for pdf_file, _ in pdf_files:
        try:
            merger.append(pdf_file)
            print(f"Appending {pdf_file} to merger.")
        except Exception as e:
            print(f"Failed to append {pdf_file}: {e}")

    output_file = os.path.join(output_path, f"{proctor_name}.pdf")
    merger.write(output_file)
    merger.close()
    print(f"Merged PDF created at: {output_file}")


def process_json_files(json_files, pdf_base_path, output_path):
    # Ensure the output directory exists at the very beginning
    if not os.path.exists(output_path):
        os.makedirs(output_path)
        print(f"Created output directory {output_path}")

    proctor_pdfs = {}

    for json_file in json_files:
        data = load_json_data(json_file)
        exam_infos = data.get('ExamInfos', [])
        for exam_info in exam_infos:
            department = exam_info['Department']
            course_code = exam_info['CourseCode']
            education_type = exam_info['EducationType']
            classrooms = exam_info['Classrooms']
            proctors = exam_info['Proctors']
            exam_datetime = parse_exam_time(exam_info['ExamDay'], exam_info['ExamMonth'], exam_info['ExamYear'],
                                            exam_info['ExamHour'], exam_info['ExamMinute'])

            department_key = 'Bilgisayar' if 'Bilgisayar' in department else 'Makine'
            education_type_key = {'Gündüz': 'Örgün', 'Gece': 'Gece', 'Gündüz ve Gece': 'Ortak'}[education_type]

            for proctor, classroom in zip(proctors, classrooms):
                pdf_files = find_pdfs_for_proctor(pdf_base_path, department_key, course_code, education_type_key,
                                                  classroom, exam_datetime)
                if pdf_files:
                    if proctor not in proctor_pdfs:
                        proctor_pdfs[proctor] = []
                    proctor_pdfs[proctor].extend(pdf_files)

    for proctor, pdf_files in proctor_pdfs.items():
        merge_pdfs(output_path, proctor, pdf_files)


# Example usage
json_files = ['computer.json', 'machine.json']
pdf_base_path = 'NKU_Exam_Tables'
output_path = 'proctors/'
process_json_files(json_files, pdf_base_path, output_path)
