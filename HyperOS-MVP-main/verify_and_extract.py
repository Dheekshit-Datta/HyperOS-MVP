import zipfile
import os
import sys

target_zip = "electron_binary_insecure.zip"
extract_path = "node_modules/electron/dist"

if not os.path.exists(target_zip):
    print(f"File {target_zip} not found.")
    sys.exit(1)

print(f"Checking {target_zip}...")
try:
    with zipfile.ZipFile(target_zip, 'r') as zip_ref:
        print("Zip file is valid. Testing first file...")
        zip_ref.testzip()
        print("Zip check passed. Extracting...")
        
        if not os.path.exists(extract_path):
            os.makedirs(extract_path)
            
        zip_ref.extractall(extract_path)
        print(f"Successfully extracted to {extract_path}")
        
except zipfile.BadZipFile:
    print("Error: The zip file is corrupt.")
    sys.exit(1)
except Exception as e:
    print(f"An error occurred: {e}")
    sys.exit(1)
