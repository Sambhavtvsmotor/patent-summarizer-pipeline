# This is the full modified scri

import pandas as pd
from transformers import pipeline
import fitz  # PyMuPDF
from PIL import Image
import io
import pytesseract
import pdfplumber
import os

print("Running the Script")


# Initialize the summarization pipeline
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Function to summarize text
def summarize_text(text, min_length=300):
    summary = summarizer(text, min_length=min_length, max_length=min_length+100, do_sample=False)
    return summary[0]['summary_text']

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    pdf_document = fitz.open(pdf_path)
    text = ""
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        text += page.get_text()
    return text

# Function to read text from a text file
def read_text_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    return text

# Function to extract images from PDF
def extract_images_from_pdf(pdf_path):
    pdf_document = fitz.open(pdf_path)
    images = []
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        image_list = page.get_images(full=True)
        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = pdf_document.extract_image(xref)
            image_bytes = base_image["image"]
            image = Image.open(io.BytesIO(image_bytes))
            images.append(image)
    return images

# Function to process images (e.g., OCR)
def process_images(images):
    processed_texts = []
    for image in images:
        text = pytesseract.image_to_string(image)
        processed_texts.append(text)
    return processed_texts

# Directory containing patent documents (PDF or text files)
input_directory = 'patent_documents'

# List to store summaries
summaries = []

# Process each file in the directory
for filename in os.listdir(input_directory):
    file_path = os.path.join(input_directory, filename)
    if filename.endswith('.pdf'):
        # Extract text from PDF
        text = extract_text_from_pdf(file_path)
        
        # Extract images from PDF and process them
        images = extract_images_from_pdf(file_path)
        image_texts = process_images(images)
        
        # Append extracted image texts to the main text
        text += " " + " ".join(image_texts)
        
        # Extract tables from PDF using pdfplumber
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    df_table = pd.DataFrame(table[1:], columns=table[0])
                    summaries.append({'Filename': filename, 'Table': df_table.to_string()})
        
    elif filename.endswith('.txt'):
        # Read text from text file
        text = read_text_file(file_path)
    else:
        continue
    
    # Summarize the extracted text
    summary = summarize_text(text)
    summaries.append({'Filename': filename, 'Summary': summary})

# Convert summaries to DataFrame
df_summaries = pd.DataFrame(summaries)

# Save the summarized data to a new Excel sheet
df_summaries.to_excel('summarized_patent_documents.xlsx', index=False)

print("Summarization complete. The summarized patent documents are saved to 'summarized_patent_documents.xlsx'.")
