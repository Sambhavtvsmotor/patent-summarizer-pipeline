import os
import fitz  # PyMuPDF
import csv
import re

def get_pdfs_from_folder(folder_path):
    return [os.path.join(folder_path, file) for file in os.listdir(folder_path) if file.lower().endswith('.pdf')]

def extract_text_from_pdf(pdf_path):
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

def extract_patent_details(text):
    details = {
        'Patent Number': '',
        'Inventor': '',
        'Assignee': '',
        'Claims': '',
        'Abstract': ''
    }

    lines = text.split('\n')

    for i, line in enumerate(lines):
        if 'Patent Number' in line:
            details['Patent Number'] = line.split(':')[-1].strip()
        elif 'Inventor' in line:
            details['Inventor'] = line.split(':')[-1].strip()
        elif 'Assignee' in line:
            details['Assignee'] = line.split(':')[-1].strip()
        elif 'Claims' in line and details['Claims'] == '':
            details['Claims'] = ' '.join(lines[i:i+5]).strip()
        elif re.search(r'\bAbstract\b', line, re.IGNORECASE) and details['Abstract'] == '':
            abstract_lines = []
            for j in range(i, min(i+50, len(lines))):
                if lines[j].strip() == '':
                    break
                abstract_lines.append(lines[j].strip())
            details['Abstract'] = ' '.join(abstract_lines)

    return details

def filter_and_extract_patent_pdfs(folder_path, output_csv):
    pdf_files = get_pdfs_from_folder(folder_path)
    with open(output_csv, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['Filename', 'Patent Number', 'Inventor', 'Assignee', 'Claims', 'Abstract'])
        writer.writeheader()
        for pdf_file in pdf_files:
            text = extract_text_from_pdf(pdf_file)
            if any(keyword in text for keyword in ['Patent Number', 'Inventor', 'Assignee', 'Claims', 'Abstract']):
                details = extract_patent_details(text)
                details['Filename'] = os.path.basename(pdf_file)
                writer.writerow(details)

# Example usage
folder_path = r'D:\Project Code\patent_documents'  # Replace with your actual folder path
output_csv = 'filtered_patents3.csv'
filter_and_extract_patent_pdfs(folder_path, output_csv)

print(f"Patent details extracted and saved to {output_csv}")
