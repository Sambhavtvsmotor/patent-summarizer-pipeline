# This Script is for WIPO 

import os
import time
import requests
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# ============================
# CONFIG
# ============================
WIPO_API_BASE = "https://patentscope.wipo.int/search/en/detail.jsf"
DOWNLOAD_DIR = "./downloads"

# ============================
# 1) Get metadata from WIPO PATENTSCOPE
# ============================
def get_wipo_metadata(pct_number):
    """
    Uses WIPO Patentscope API to get basic metadata.
    Note: WIPO doesn't have an official open JSON API for full text,
    so we simulate a basic request.
    """
    # This is a simplified example: in reality you would scrape the detail page or use XML
    search_url = f"https://patentscope.wipo.int/search/en/detail.jsf?docId={pct_number}"
    print(f"Metadata page: {search_url}")
    
    # There is no direct open API for JSON metadata; you may need to parse XML if needed.
    metadata = {
        "PCT_Number": pct_number,
        "Detail_URL": search_url
    }
    return metadata

# ============================
# 2) Use Selenium to download PDF
# ============================
def download_wipo_pdf(pct_number, download_dir=DOWNLOAD_DIR):
    options = webdriver.ChromeOptions()
    prefs = {
        "download.default_directory": os.path.abspath(download_dir),
        "download.prompt_for_download": False,
        "plugins.always_open_pdf_externally": True
    }
    options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        search_url = f"https://patentscope.wipo.int/search/en/detail.jsf?docId={pct_number}"
        driver.get(search_url)
        time.sleep(5)

        # Click "Download" button
        download_button = driver.find_element(By.LINK_TEXT, "Download")
        download_button.click()
        time.sleep(3)

        # Click "International Publication"
        int_pub_link = driver.find_element(By.XPATH, "//a[contains(text(), 'International Publication')]")
        int_pub_link.click()
        print(f"Downloading PDF for {pct_number}...")

        time.sleep(10)  # Wait for download

        pdf_filename = f"{pct_number}.pdf"
        return pdf_filename

    except Exception as e:
        print(f"Error: {e}")
        return None

    finally:
        driver.quit()
        print("Browser closed.")

# ============================
# 3) Combine metadata & PDF info, save to Excel
# ============================
def save_metadata_to_excel(records, output_file="wipo_patent_data.xlsx"):
    df = pd.DataFrame(records)
    df.to_excel(output_file, index=False)
    print(f"Metadata saved to {output_file}")

# ============================
# MAIN
# ============================
if __name__ == "__main__":
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    # Example list of PCT publication numbers
    pct_numbers = ["WO2023123456"]  # Replace with real PCT numbers

    all_records = []

    for pct_number in pct_numbers:
        metadata = get_wipo_metadata(pct_number)
        pdf_file = download_wipo_pdf(pct_number)
        metadata["PDF_File"] = pdf_file
        all_records.append(metadata)

    save_metadata_to_excel(all_records)
