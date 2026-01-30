import zipfile
import os
import sys

dest = "electron_binary_insecure.zip"
extract_path = "node_modules/electron/dist"

try:
    if not os.path.exists(extract_path):
        os.makedirs(extract_path)
        
    print(f"Extracting {dest} to {extract_path}...")
    with zipfile.ZipFile(dest, 'r') as zip_ref:
        zip_ref.extractall(extract_path)
    
    print("Extraction successful. Electron binary is ready.")
    
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
