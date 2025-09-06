import os
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv

# Import ChromeDriverManager from webdriver_manager
from webdriver_manager.chrome import ChromeDriverManager

# Load .env file
load_dotenv()

# Get endpoint from .env
ENDPOINT = os.getenv("ENDPOINT_P1")

# Directories
dirname = os.path.dirname(os.path.abspath(__file__))
download_dir = os.path.join(dirname, "zip-dl")

def extract_hybris():
    options = Options()
    options.add_argument("--headless=new")  # modern headless mode
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "safebrowsing.enabled": True
    }
    options.add_experimental_option("prefs", prefs)

    # --- CHANGES START HERE ---
    # Use ChromeDriverManager to automatically handle the driver path.
    # It will download the correct chromedriver version if it's not present.
    service = Service(ChromeDriverManager().install())
    
    # Use the service object to create the Chrome driver instance.
    driver = webdriver.Chrome(service=service, options=options)
    # --- CHANGES END HERE ---

    driver.get(ENDPOINT)
    time.sleep(5)

    source = BeautifulSoup(driver.page_source, "html.parser")
    print("\n=== PAGE SOURCE START ===\n")
    print(source.prettify())
    print("\n=== PAGE SOURCE END ===\n")

    driver.quit()

if __name__ == "__main__":
    extract_hybris()