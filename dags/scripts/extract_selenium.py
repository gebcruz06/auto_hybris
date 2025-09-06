from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import zipfile
import time
import os
from dotenv import load_dotenv
import tempfile

# Load .env file
load_dotenv()

HYBRIS_USER = os.getenv('HYBRIS_USER_P1')
HYBRIS_PW = os.getenv('HYBRIS_PW_P1')
ENDPOINT = os.getenv('ENDPOINT_P1')

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

    # Use a unique temp Chrome profile for each run (fixes SessionNotCreatedException)
    temp_profile = tempfile.mkdtemp()
    options.add_argument(f"--user-data-dir={temp_profile}")

    # Use webdriver-manager to automatically download and install the correct ChromeDriver
    return webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

def login(driver, HYBRIS_USER, HYBRIS_PW):
    try:
        wait = WebDriverWait(driver, 20) # Set a generous wait time

        # Wait for and find the username input field
        user = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/form/div/ul/li[1]/input')))
        user.send_keys(HYBRIS_USER)
        print('username entered')

        # Wait for and find the password input field
        pw = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/form/div/ul/li[2]/input')))
        pw.send_keys(HYBRIS_PW)
        print('password entered')

        # Wait for and click the login button
        login_button = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/form/div/ul/li[4]/button')))
        login_button.click()
        print('Login button clicked')

    except TimeoutException:
        print("Timeout waiting for login elements. Please check the page HTML or your XPaths.")
        # Raise the exception to fail the task gracefully
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
    """
    try:
        # Wait for the download section to be present
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div[1]/div')))
        
        # Wait for the download button to be clickable
        download_button = WebDriverWait(driver, 200).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/div[2]/div/div[1]/div[1]/form/fieldset/p/input[1]')))
        download_button.click()

        # Wait for the zip file link to appear
        zip_file_element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div[2]/div/div[3]/ul/li[1]/a')))
        
        print(zip_file_element.get_attribute('href'))
        driver.execute_script("arguments[0].scrollIntoView();", zip_file_element)
        zip_file_name = zip_file_element.text
        zip_file_element.click()

        print(f"Waiting for {zip_file_name} to download...")
        
        # Construct the expected file path
        expected_file_path = os.path.join(dirname, zip_file_name)

        # Wait for the file to be present and not be a .tmp file
        max_wait_time = 300  # 5 minutes, adjust as needed
        start_time = time.time()
        
        while not os.path.exists(expected_file_path):
            if time.time() - start_time > max_wait_time:
                raise TimeoutError(f"Download of {zip_file_name} timed out.")
            
            # Check for .tmp files to provide more info
            tmp_file = expected_file_path + ".tmp"
            if os.path.exists(tmp_file):
                print(f"Temporary file {tmp_file} exists. Waiting for download to complete.")
            
            time.sleep(2) # Check every 2 seconds

        print(f'{zip_file_name} downloaded')
        return zip_file_name

    except TimeoutException:
        print("Timeout waiting for a page element. The download process may not have started.")
        # Return None to signal failure to the calling function
        return None
    
    except Exception as e:
        print(f"An error occurred during the download process: {e}")
        return None


def extract_hybris():
    # Define the path for the downloads and unzipped files
    zip_dir = os.path.join(os.getcwd(), 'zip-dl')

    # Create the directory if it does not exist
    os.makedirs(zip_dir, exist_ok=True)
    print(f"Download and extraction directory: {zip_dir}")
    
    url = ENDPOINT
    driver = selenium_webdriver(zip_dir) # Pass the new download directory
    driver.get(url)

    # login to hybris just once before the main loop
    try:
        login(driver, HYBRIS_USER, HYBRIS_PW)

        # Wait for the navigation menu to appear after login
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/header/div[3]/nav[1]/ul/li[4]/a')))
        driver.find_element(By.XPATH, '/html/body/div[2]/header/div[3]/nav[1]/ul/li[4]/a').click()
        
        # Wait for the impex link to be clickable
        impex = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/header/div[3]/nav[5]/div/ul/li[4]/a')))
        impex.click()
        print('Navigated to Impex Export page.')

        # Wait for the page content to load after navigating
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div[2]/div/div[1]/div[1]/form/fieldset/div[1]/div[1]/div[6]/div[1]/div/div/div/div[5]/div/pre')))

    except Exception as e:
        print(f"An error occurred during initial navigation: {e}")
        # Optionally, take a screenshot for debugging
        driver.save_screenshot("navigation_error.png")
        print('\n')
        source = BeautifulSoup(driver.page_source, 'html.parser')
        print(source.prettify()) # Use prettify() for readable HTML
        driver.quit()
        return []

    list_executable = [
        '''
        # ---- Extension: core ---- Type: OrderEntry ----
        "#% impex.setTargetFile( ""OrderEntry.csv"" );"
        INSERT_UPDATE OrderEntry; &Item; basePrice; calculated; creationtime[forceWrite = true, dateformat = HH:mm:ss dd.MM.yyyy]; deliveryAddress(&Item); entryNumber[unique = true]; giveAway[allownull = true]; info; modifiedtime[dateformat = HH:mm:ss dd.MM.yyyy]; order(code, versionID)[forceWrite = true, unique = true, allownull = true]; product(catalogVersion(catalog(id), version), code)[allownull = true]; quantityStatus(code, itemtype(code)); quantityUpdatedTime[dateformat = HH:mm:ss dd.MM.yyyy]; quantity[allownull = true]; rejected[allownull = true]; taxValues; taxValuesInternal; totalPrice; unit(code)[allownull = true];preorder
        "#% impex.exportItems( ""OrderEntry"" , false );"
        ''',
        # ... (rest of your list_executable)
        '''
        # ---- Extension: core ---- Type: Address ----
        # Addresses for the B2BUnits only
        $query= select {a.pk} from {Address as a join B2BUnit as b on {a.owner}={b.pk}}
        "#% impex.setTargetFile(""Address.csv"");"
        insert Address;&Item;billingAddress[allownull=true];billingEnquiry[allownull=true];building;cell-phone;company;contactAddress[allownull=true];country(isocode);creationtime[forceWrite=true,dateformat=dd.MM.yyyy hh:mm:ss];duplicate;email;fax;firstname;gender(code,itemtype(code));lastname;middlename;middlename2;modifiedtime[dateformat=dd.MM.yyyy hh:mm:ss];original(&Item)[forceWrite=true];partsEnquiry[allownull=true];phone1;phone2;pobox;postalcode;publicKey;region(country(isocode),isocode);remarks;salesEnquiry[allownull=true];shippingAddress[allownull=true];streetname;streetnumber;title(code);town;unloadingAddress[allownull=true];visibleInAddressBook;pk
        #% impex.exportItemsFlexibleSearch("$query ");
        ''',
        '''
        # ---- Extension: b2bcommerce ---- Type: B2BCustomer ----
        $query= SELECT {u:pk},{u:active}, {u:apigeeToken}, {u:authorizedToUnlockPages}, {u:backOfficeLoginDisabled}, FORMAT({u:creationtime},'dd.MM.yyyy HH:mm:ss'), {u:customerID}, FORMAT({u:deactivationDate},'dd.MM.yyyy HH:mm:ss'), {u:defaultB2BUnit}, {u:description}, {u:emailPreference}, {u:email}, {u:firstName}, {u:forgotPasswordAttemptCount}, {u:hmcLoginDisabled}, FORMAT({u:lastLogin},'dd.MM.yyyy HH:mm:ss'), {u:lastName}, {u:loginDisabled}, FORMAT({u:modifiedtime},'dd.MM.yyyy HH:mm:ss'), {u:name}, {u:originalUid}, {u:owner}, {u:sessionCurrency}, {u:sessionLanguage}, {u:smsPreference}, {u:title}, {u:type}, {u:uid}, {u:undecoratedUid} FROM { UserGroup as ug JOIN PrincipalGroupRelation as rel ON {ug:PK} = {rel:target} JOIN B2BCustomer AS u ON {rel:source} = {u:PK} } WHERE {ug:uid}='retaileradmingroup'

        "#% impex.setTargetFile(""B2BCustomer.csv"");"
        insert_update B2BCustomer;&Item;active[allownull=true];apigeeToken;authorizedToUnlockPages[allownull=true];backOfficeLoginDisabled;creationtime[forceWrite=true,dateformat=dd.MM.yyyy HH:mm:ss];customerID;deactivationDate[dateformat=dd.MM.yyyy HH:mm:ss];defaultB2BUnit(uid);description;emailPreference;email[allownull=true];firstName;forgotPasswordAttemptCount;hmcLoginDisabled;lastLogin[dateformat=dd.MM.yyyy HH:mm:ss];lastName;loginDisabled[allownull=true];modifiedtime[dateformat=dd.MM.yyyy HH:mm:ss];name;originalUid;owner(&Item)[allownull=true,forceWrite=true];sessionCurrency(isocode);sessionLanguage(isocode);smsPreference;title(code);type(code,itemtype(code));uid[unique=true,allownull=true];undecoratedUid
        #% impex.exportItemsFlexibleSearch("$query ");
        ''',
        '''
        # ---- Extension: b2bcommerce ---- Type: B2BUnit ----
        "#% impex.setTargetFile( ""B2BUnit.csv"" );"
        insert_update B2BUnit;&Item;adpAccountCode;abnNumber;accountNumber;acnNumber;active[allownull=true];addresses(pk)[collection-delimiter=' '];billingAddress(pk);buyer[allownull=true];carrier[allownull=true];closingHours(code,itemtype(code));contact(uid);country(isocode);creationtime[forceWrite=true,dateformat=dd.MM.yyyy hh:mm:ss];description;locName[lang=en];manufacturer[allownull=true];modifiedtime[dateformat=dd.MM.yyyy hh:mm:ss];name;openingHours(code,itemtype(code));owner(&Item)[allownull=true,forceWrite=true];path;pointOfService(name);readableLanguages(isocode);reportingOrganization(uid);shippingAddress(pk);supplier[allownull=true];tradingName;uid[unique=true,allownull=true];writeableLanguages(isocode);userPriceGroup(code,itemtype(code));pk;partsClubMembershipNumber
        "#% impex.exportItems( ""B2BUnit"" , false );"
        ''',
        '''
        # ---- Extension: core ---- Type: Order ----
        "#% impex.setTargetFile( ""Order.csv"" );"
        insert_update Order;&Item;Unit(uid);calculated;code[unique=true];consentReference;creationtime[forceWrite=true,dateformat=HH:mm:ss dd.MM.yyyy];currency(isocode)[allownull=true];date[allownull=true,dateformat=HH:mm:ss dd.MM.yyyy];deliveryAddress(&Item);deliveryCost;deliveryMode(code);description;discountsIncludeDeliveryCost[allownull=true];discountsIncludePaymentCost[allownull=true];expirationTime[dateformat=HH:mm:ss dd.MM.yyyy];fraudulent;guid;invoiceNo;language(isocode);locale;modifiedtime[dateformat=HH:mm:ss dd.MM.yyyy];name;net[allownull=true];paymentAddress(&Item);paymentCost;paymentMode(code);paymentType(code,itemtype(code));placedBy(uid);potentiallyFraudulent;purchaseOrderNumber;salesApplication(code,itemtype(code));sellerAccount(uid);site(uid);status(code,itemtype(code));statusInfo;store(uid);subtotal;totalDiscounts;totalPrice;totalTax;totalTaxValues;totalTaxValuesInternal;user(uid)[allownull=true,alias=users];versionID[forceWrite=true,unique=true];workflow(code);isMsCouponEligible
        "#% impex.exportItems( ""Order"" , false );"
        ''',
        '''
        # ---- Extension: basecommerce ---- Type: OrderEntryReturnRecordEntry ----
        "#% impex.setTargetFile( ""OrderEntryReturnRecordEntry.csv"" );"
        insert OrderEntryReturnRecordEntry;&Item;code[allownull=true,forceWrite=true];creationtime[forceWrite=true,dateformat=dd.MM.yyyy HH:mm:ss];expectedQuantity;modificationRecordEntry(code)[allownull=true];modifiedtime[dateformat=dd.MM.yyyy HH:mm:ss];notes;orderEntry(entryNumber,order(code,versionID));originalOrderEntry(entryNumber,order(code,versionID));owner(&Item)[allownull=true,forceWrite=true];returnedQuantity
        "#% impex.exportItems( ""OrderEntryReturnRecordEntry"" , false );"
        ''',
        '''
        # ---- Extension: basecommerce ---- Type: RefundEntry ----
        "#% impex.setTargetFile( ""RefundEntry.csv"" );"
        insert RefundEntry;&Item;action(code,itemtype(code))[allownull=true];amount;creationtime[forceWrite=true,dateformat=dd.MM.yyyy HH:mm:ss];expectedQuantity;modifiedtime[dateformat=dd.MM.yyyy HH:mm:ss];notes;orderEntry(entryNumber)[allownull=true];owner(&Item)[allownull=true,forceWrite=true];reachedDate[dateformat=dd.MM.yyyy HH:mm:ss];reason(code,itemtype(code))[allownull=true];receivedQuantity;refundedDate[dateformat=dd.MM.yyyy HH:mm:ss];returnRequest(code);returnRequestPOS;status(code,itemtype(code))[allownull=true];tax
        "#% impex.exportItems( ""RefundEntry"" , false );"
        ''',
        '''
        # ---- Extension: basecommerce ---- Type: OrderReturnRecord ----
        "#% impex.setTargetFile( ""OrderReturnRecord.csv"" );"
        insert_update OrderReturnRecord;&Item;creationtime[forceWrite=true,dateformat=dd.MM.yyyy HH:mm:ss];identifier[unique=true];inProgress[allownull=true];modifiedtime[dateformat=dd.MM.yyyy HH:mm:ss];order(code,versionID)[allownull=true];owner(&Item)[allownull=true,forceWrite=true]
        "#% impex.exportItems( ""OrderReturnRecord"" , false );"
        ''',
        '''
        # ---- Extension: basecommerce ---- Type: ImageNames ----
        "#% impex.setTargetFile( ""MediaContainer.csv"" );"
        insert_update MediaContainer;&Item;catalogVersion(catalog(id),version)[unique=true,allownull=true];conversionGroup(&Item);creationtime[forceWrite=true,dateformat=dd.MM.yyyy HH:mm:ss a];modifiedtime[dateformat=dd.MM.yyyy HH:mm:ss];owner(&Item)[allownull=true,forceWrite=true];qualifier[unique=true,allownull=true]
        "#% impex.exportItems( ""MediaContainer"" , false );"
        ''',
        '''
        # ----Public Holiday HK:----
        $query=select {pk},{uid}, {date} from {DateSetting} where {uid} like '%hk%'
        "#% impex.setTargetFile(""PublicHolidayHK.csv"");"
        INSERT_UPDATE DateSetting;pk;uid[unique = true];date[dateformat=dd/MM/yyyy];
        #% impex.exportItemsFlexibleSearch("$query ");
        ''',
        '''
        # ----Public Holiday SG:----
        $query=select {pk},{uid}, {date} from {DateSetting} where {uid} like '%sg%'
        "#% impex.setTargetFile(""PublicHolidaySG.csv"");"
        INSERT_UPDATE DateSetting;pk;uid[unique = true];date[dateformat=dd/MM/yyyy];
        #% impex.exportItemsFlexibleSearch("$query ");
        ''',
        '''
        # ---- Extension: core ---- Type: PhoneContactInfo ----
        "#% impex.setTargetFile( ""PhoneContactInfo.csv"" );"
        insert PhoneContactInfo;&Item;code[allownull=true];creationtime[forceWrite=true,dateformat=dd.MM.yyyy hh:mm:ss];modifiedtime[dateformat=dd.MM.yyyy hh:mm:ss];owner(&Item)[allownull=true,forceWrite=true];phoneNumber[allownull=true];type(code,itemtype(code))[allownull=true];user(uid)[alias=users,allownull=true];userPOS
        "#% impex.exportItems( ""PhoneContactInfo"" , false );"
        ''',
        '''
        # ---- Extension: paymentstandard ---- Type: StandardPaymentMode ----
        "#% impex.setTargetFile( ""StandardPaymentMode.csv"" );"
        insert_update StandardPaymentMode;&Item;active[allownull=true];code[unique=true,allownull=true];creationtime[forceWrite=true,dateformat=dd.MM.yyyy hh:mm:ss];default;modifiedtime[dateformat=dd.MM.yyyy hh:mm:ss];net[allownull=true];owner(&Item)[allownull=true,forceWrite=true];paymentInfoType(code)[allownull=true];paymentProvider(code,itemtype(code));supportedUserPriceGroups(code,itemtype(code))
        "#% impex.exportItems( ""StandardPaymentMode"" , false );"
        ''',
    ]
    
    zip_names = []
    try:
        for text_input in list_executable:
            # input text and validate
            input_text_and_validate(driver, text_input)

            # download the validated zip file, passing the dirname
            zip_name = download_zip(driver, zip_dir)
            
            if zip_name:
                # unzip the downloaded file
                zip_file_path = os.path.join(zip_dir, zip_name)
                with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                    zip_name_fldr = zip_name.split('.')[0]
                    # Extract files to the zip_dir
                    zip_ref.extractall(zip_dir) 
                    zip_names.append(zip_name_fldr)
                print(f"Unzipped files from {zip_name} to {zip_dir}")
                
                # Clean up the downloaded zip file after extraction
                os.remove(zip_file_path)

    except Exception as e:
        print(f"An error occurred: {e}")
        driver.quit()
        return zip_names # Return whatever was collected so far in case of error

    driver.quit()

    return zip_names

if __name__ == "__main__":
    results = extract_hybris()
    if results:
        print("Extraction completed:", results)
    else:
        print("Extraction failed.")