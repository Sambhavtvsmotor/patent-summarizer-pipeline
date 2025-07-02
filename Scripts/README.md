# 📄 Patent Pipeline

## ✅ Overview

This Python pipeline:
- Accepts one or multiple **patent numbers or application numbers**
- Fetches complete patent details using **SerpApi Google Patents**
- Extracts Title, Abstract, Summary, Claims, CPC Classifications, Inventors, PDF Link
- Adds cleaned text fields for NLP: **Cleaned Abstract**, **Cleaned Summary**, **Cleaned Claims**
- Appends results to a master **Excel file** `output/patents_details.xlsx`
- Creates a timestamped backup every run for safety

## 📌 Folder Structure

Python Code/
├── myenv/
├── patent_documents/
├── Rough/
├── Scripts/
│ ├── script.py
│ ├── output/
│ │ └── patents_details.xlsx
│ ├── requirements.txt
│ └── README.md


## ✅ How to run

1. Activate your virtual environment:
      	.\myenv\Scripts\activate   # Windows
   	source myenv/bin/activate  # Linux/Mac

2. Install dependencies:
	pip install -r requirements.txt

3. Run:
	python script.py

Input one or more patent/application numbers separated by commas.

✅ Dependencies
serpapi for Google Patents search

pandas for data handling

openpyxl for Excel export

nltk or spacy for text cleaning


📌 Notes
Always close patents_details.xlsx before running the script.

Stop words are defined in patent_stop_words — update this as you refine your NLP pipeline.

Backups are saved in output/ with timestamps.