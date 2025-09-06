from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time
import os

# Import ChromeDriverManager from webdriver_manager
from webdriver_manager.chrome import ChromeDriverManager

# Directories
dirname = os.path.dirname(os.path.abspath(__file__))
download_dir = os.path.join(dirname, 'zip-dl')

def get_my_ip():
    # Set up Chrome options
    options = Options()
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    options.add_experimental_option("prefs", prefs)
    options.add_argument("--headless")  # remove if you want to see the browser
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # --- CHANGES START HERE ---
    # Use ChromeDriverManager to automatically handle the driver path
    # It will download the correct version of chromedriver if it's not present
    # and return the path to it. This line replaces the platform check and hardcoded paths.
    service = Service(ChromeDriverManager().install())
    
    # Set up Chrome driver with the automatically managed service
    driver = webdriver.Chrome(service=service, options=options)
    # --- CHANGES END HERE ---

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