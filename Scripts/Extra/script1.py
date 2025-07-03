from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

def download_patent_pdf(patent_number, download_dir="./downloads"):
    # Setup Chrome options
    options = webdriver.ChromeOptions()
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "plugins.always_open_pdf_externally": True
    }
    options.add_experimental_option("prefs", prefs)

    # Start Chrome
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        url = f"https://patents.google.com/patent/{patent_number}/en"
        driver.get(url)
        time.sleep(3)

        # Find the "Download PDF" link
        pdf_link = driver.find_element(By.LINK_TEXT, "Download PDF")
        pdf_link.click()
        print(f"Downloading PDF for patent {patent_number}...")

        # Wait for download to finish
        time.sleep(10)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    patent_number = "EP3816017B1"  # Replace with your patent number
    download_patent_pdf(patent_number)
