from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
import time
import os

# Import GeckoDriverManager from webdriver_manager
from webdriver_manager.firefox import GeckoDriverManager

# Directories
dirname = os.path.dirname(os.path.abspath(__file__))
download_dir = os.path.join(dirname, 'zip-dl')

def test_browser():
    # Set up Firefox options
    options = Options()
    options.set_preference("browser.download.folderList", 2)
    options.set_preference("browser.download.dir", download_dir)  # custom download dir
    options.set_preference("browser.download.manager.showWhenStarting", False)
    # This preference prevents Firefox from showing a download dialog for these file types
    options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/zip, application/octet-stream")
    
    options.add_argument("-headless")  # use headless mode
  
    # Use GeckoDriverManager to automatically handle the driver path.
    service = Service(GeckoDriverManager().install())
    
    # Use the service object to create the Firefox driver instance.
    driver = webdriver.Firefox(service=service, options=options)

    url = 'https://www.google.com'
    driver.get(url)

    # Wait for the page to load
    time.sleep(5)
    print('Page loaded successfully')
    print(f"Script directory: {dirname}")
    print(f"Download directory: {download_dir}")
    
    # Print the browser version to confirm it's running
    print(f"Browser version: {driver.capabilities['browserVersion']}")
    
    driver.quit()
    return True

if __name__ == "__main__":
    test_browser()
