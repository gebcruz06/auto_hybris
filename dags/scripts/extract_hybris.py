import os
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from dotenv import load_dotenv

# Import GeckoDriverManager from webdriver_manager
from webdriver_manager.firefox import GeckoDriverManager

# Load .env file
load_dotenv()

# Get endpoint from .env
ENDPOINT = os.getenv("ENDPOINT_P1")

# Directories
dirname = os.path.dirname(os.path.abspath(__file__))
download_dir = os.path.join(dirname, "zip-dl")

def extract_hybris():
    options = Options()
    options.add_argument("-headless")  # modern headless mode
    options.set_preference("browser.download.folderList", 2)
    options.set_preference("browser.download.dir", download_dir)
    options.set_preference("browser.download.manager.showWhenStarting", False)
    options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/zip, application/octet-stream")

    # Use GeckoDriverManager to automatically handle the driver path.
    service = Service(GeckoDriverManager().install())
    
    # Use the service object to create the Firefox driver instance.
    driver = webdriver.Firefox(service=service, options=options)

    driver.get(ENDPOINT)
    time.sleep(5)

    source = BeautifulSoup(driver.page_source, "html.parser")
    print("\n=== PAGE SOURCE START ===\n")
    print(source.prettify())
    print("\n=== PAGE SOURCE END ===\n")

    driver.quit()

if __name__ == "__main__":
    extract_hybris()
