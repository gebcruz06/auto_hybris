import os
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceNotFoundError

load_dotenv()

def upload_extract_p1():
    BLOB_CONN = os.getenv('BLOB_CONN')

    if not BLOB_CONN:
        print("Error: BLOB_CONN environment variable not found.")
        return False

    print("Starting to upload the files to Azure Blob Storage...")

    # Create the BlobServiceClient object
    try:
        blob_service_client = BlobServiceClient.from_connection_string(BLOB_CONN)
    except ValueError as e:
        print(f"Error: Invalid connection string. {e}")
        return False

    local_file_path = 'zip-dl'
    # prod
    container_name = 'azure-data-factory'
    directory_name = 'hybris/impex'
    file_list = [
        'OrderEntry.csv', 'Address.csv', 'B2BCustomer.csv', 'B2BUnit.csv',
        'Order.csv', 'OrderEntryReturnRecordEntry.csv', 'RefundEntry.csv',
        'OrderReturnRecord.csv', 'MediaContainer.csv', 'PublicHolidayHK.csv',
        'PublicHolidaySG.csv', 'PhoneContactInfo.csv', 'StandardPaymentMode.csv'
    ]
    
    upload_success = True
    for filename in file_list:
        local_file_full_path = os.path.join(local_file_path, filename)
        
        if not os.path.exists(local_file_full_path):
            print(f"Skipping file: {filename} - File not found at {local_file_full_path}")
            upload_success = False
            continue

        print('Uploading file: ' + filename + ' to Azure Blob Storage...')
        try:
            container_client = blob_service_client.get_container_client(container_name)
            blob_client = container_client.get_blob_client(os.path.join(directory_name, filename))
            
            with open(local_file_full_path, "rb") as data:  # Use "rb" for binary mode
                blob_client.upload_blob(data, overwrite=True)
            
            print('The file is uploaded successfully!!!')
        except ResourceNotFoundError:
            print(f"Error: Azure container '{container_name}' not found.")
            upload_success = False
            break
        except Exception as e:
            print(f"An unexpected error occurred during upload for {filename}: {e}")
            upload_success = False
            break

    return upload_success

if __name__ == "__main__":
    results = upload_extract_p1()
    if results:
        print("Upload completed successfully.")
    else:
        print("Upload failed or some files were not found.")