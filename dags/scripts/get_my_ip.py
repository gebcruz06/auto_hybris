from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
import time
import os

# Import GeckoDriverManager from webdriver_manager
from webdriver_manager.firefox import GeckoDriverManager

# Directories
dirname = os.path.dirname(os.path.abspath(__file__))
download_dir = os.path.join(dirname, 'zip-dl')

def get_my_ip():
    # Set up Firefox options
    options = Options()
    options.set_preference("browser.download.folderList", 2)
    options.set_preference("browser.download.dir", download_dir)
    options.set_preference("browser.download.manager.showWhenStarting", False)
    options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/zip, application/octet-stream")
    options.add_argument("-headless")  # remove if you want to see the browser

    # Use GeckoDriverManager to automatically handle the driver path
    service = Service(GeckoDriverManager().install())
    
    # Set up Firefox driver with the automatically managed service
    driver = webdriver.Firefox(service=service, options=options)

    url = 'https://whatismyipaddress.com/'

    # Open the URL
    driver.get(url)

    # Wait for the page to load
    time.sleep(5)
    print('Page loaded successfully')

    # Extract IP addresses
    try:
        my_ipv4 = driver.find_element(
            By.XPATH,
            '/html/body/div[1]/div/div/div/div/article/div/div/div[1]/div/div[2]/div/div/div/div/div/div[2]/div[1]/div[1]/p[2]/span[2]/a'
        ).text
        print('My IPv4 Address:', my_ipv4)
    except:
        print("Could not find IPv4 element, skipping.")

    try:
        my_ipv6 = driver.find_element(
            By.XPATH,
            '/html/body/div[1]/div/div/div/div/article/div/div/div[1]/div/div[2]/div/div/div/div/div/div[2]/div[1]/div[1]/p[3]/span[2]'
        ).text
        print('My IPv6 Address:', my_ipv6)
    except:
        print("Could not find IPv6 element, skipping.")

    time.sleep(2)

    # Close the driver
    driver.quit()


if __name__ == "__main__":
    get_my_ip()
