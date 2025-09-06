@ -22,24 +22,33 @@ ENDPOINT = os.getenv('ENDPOINT_P1')

def selenium_webdriver(dirname):
    options = Options()
    # Set download directory
    options.add_experimental_option("prefs", {
        "download.default_directory": dirname,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })
    
    # Run in headless mode (no visible browser window)
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # Setting a consistent window size is good practice for headless mode
    options.add_argument("--window-size=1920,1080")

    # Use a unique temp Chrome profile for each run (fixes SessionNotCreatedException)
    temp_profile = tempfile.mkdtemp()
    options.add_argument(f"--user-data-dir={temp_profile}")

    # Use webdriver-manager to automatically download and install the correct ChromeDriver
    return webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    
    # --- CRITICAL FIX FOR DOWNLOADS IN DOCKER HEADLESS MODE ---
    # Use the DevTools Protocol to set the download behavior.
    # This is more reliable than the experimental `prefs` option in headless environments.
    driver.execute_cdp_cmd(
        "Page.setDownloadBehavior", 
        {
            "behavior": "allow", 
            "downloadPath": dirname
        }
    )
    
    return driver

def login(driver, HYBRIS_USER, HYBRIS_PW):
    try:
@ -66,19 +75,19 @@ def login(driver, HYBRIS_USER, HYBRIS_PW):
        raise

def input_text_and_validate(driver, text_input):
    # This function already uses a wait, so it's good to go.
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div[2]/div/div[1]/div[1]/form/fieldset/div[1]/div[1]/div[6]/div[1]/div/div/div/div[5]/div/pre'))).click()
    elem = driver.switch_to.active_element
    elem.send_keys(text_input)

    # Validate button
    # Add a wait for the validate button to be clickable
    validate_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/div[2]/div/div[1]/div[1]/form/fieldset/p/input[2]')))
    validate_button.click()

def download_zip(driver, dirname):
    """
    Waits for the download to start and complete.
    This function now relies on the DevTools protocol to save the file
    to the specified 'dirname'.
    """
    try:
        # Wait for the download section to be present
@ -91,7 +100,7 @@ def download_zip(driver, dirname):
        # Wait for the zip file link to appear
        zip_file_element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div[2]/div/div[3]/ul/li[1]/a')))
        
        print(zip_file_element.get_attribute('href'))
        print(f"File to download: {zip_file_element.text}")
        driver.execute_script("arguments[0].scrollIntoView();", zip_file_element)
        zip_file_name = zip_file_element.text
        zip_file_element.click()
@ -101,23 +110,24 @@ def download_zip(driver, dirname):
        # Construct the expected file path
        expected_file_path = os.path.join(dirname, zip_file_name)

        # Wait for the file to be present and not be a .tmp file
        # Wait for the file to be present and its size to stabilize (indicating completion)
        max_wait_time = 300  # 5 minutes, adjust as needed
        start_time = time.time()
        
        while not os.path.exists(expected_file_path):
            if time.time() - start_time > max_wait_time:
                raise TimeoutError(f"Download of {zip_file_name} timed out.")
            
            # Check for .tmp files to provide more info
            tmp_file = expected_file_path + ".tmp"
            if os.path.exists(tmp_file):
                print(f"Temporary file {tmp_file} exists. Waiting for download to complete.")
        while time.time() - start_time < max_wait_time:
            if os.path.exists(expected_file_path):
                # Check for file size to stop growing (an indication of completion)
                initial_size = os.path.getsize(expected_file_path)
                time.sleep(1)
                current_size = os.path.getsize(expected_file_path)
                
                if initial_size == current_size and current_size > 0:
                    print(f'{zip_file_name} downloaded successfully.')
                    return zip_file_name
            
            time.sleep(2) # Check every 2 seconds

        print(f'{zip_file_name} downloaded')
        return zip_file_name
        raise TimeoutError(f"Download of {zip_file_name} timed out or was not fully completed.")

    except TimeoutException:
        print("Timeout waiting for a page element. The download process may not have started.")
@ -128,7 +138,6 @@ def download_zip(driver, dirname):
        print(f"An error occurred during the download process: {e}")
        return None


def extract_hybris():
    # Define the path for the downloads and unzipped files
    zip_dir = os.path.join(os.getcwd(), 'zip-dl')
@ -174,7 +183,6 @@ def extract_hybris():
        INSERT_UPDATE OrderEntry; &Item; basePrice; calculated; creationtime[forceWrite = true, dateformat = HH:mm:ss dd.MM.yyyy]; deliveryAddress(&Item); entryNumber[unique = true]; giveAway[allownull = true]; info; modifiedtime[dateformat = HH:mm:ss dd.MM.yyyy]; order(code, versionID)[forceWrite = true, unique = true, allownull = true]; product(catalogVersion(catalog(id), version), code)[allownull = true]; quantityStatus(code, itemtype(code)); quantityUpdatedTime[dateformat = HH:mm:ss dd.MM.yyyy]; quantity[allownull = true]; rejected[allownull = true]; taxValues; taxValuesInternal; totalPrice; unit(code)[allownull = true];preorder
        "#% impex.exportItems( ""OrderEntry"" , false );"
        ''',
        # ... (rest of your list_executable)
        '''
        # ---- Extension: core ---- Type: Address ----
        # Addresses for the B2BUnits only
