from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time
import os

# Import ChromeDriverManager from webdriver_manager
from webdriver_manager.chrome import ChromeDriverManager

# Directories
dirname = os.path.dirname(os.path.abspath(__file__))
download_dir = os.path.join(dirname, 'zip-dl')

def test_browser():
    # Set up Chrome options
    options = Options()
    prefs = {
        "download.default_directory": download_dir,  # custom download dir
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    options.add_experimental_option("prefs", prefs)
    options.add_argument("--headless=new")  # use headless mode
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")

    # --- CHANGES START HERE ---
    # Use ChromeDriverManager to automatically handle the driver path.
    # It will download the correct chromedriver version if it's not present.
    service = Service(ChromeDriverManager().install())
    
    # Use the service object to create the Chrome driver instance.
    driver = webdriver.Chrome(service=service, options=options)
    # --- CHANGES END HERE ---

    url = 'https://www.google.com'
    driver.get(url)

    # Wait for the page to load
    time.sleep(5)
    print('Page loaded successfully')
    print(f"Script directory: {dirname}")
    print(f"Download directory: {download_dir}")
    
    # We can no longer print the hardcoded driver_path, but we can confirm it's running
    print(f"Driver version: {driver.capabilities['chrome']['chromedriverVersion']}")
    
    driver.quit()
    return True


if __name__ == "__main__":
    test_browser()