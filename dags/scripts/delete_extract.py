import os, glob

def delete_extract_p1():
    directory = "zip-dl"
    file_patterns = [
        '*.csv', '*.zip', '*.impex'
    ]
    for pattern in file_patterns:
        # Construct the full search pattern
        search_pattern = os.path.join(directory, pattern)
        
        # Use glob to find all files matching the pattern
        files_to_delete = glob.glob(search_pattern)
        
        # Iterate over each found file and delete it
        for file_path in files_to_delete:
            try:
                os.remove(file_path)
                print(f"Deleted: {file_path}")
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")


if __name__ == "__main__":
    delete_extract_p1()
    print('Deleted files')