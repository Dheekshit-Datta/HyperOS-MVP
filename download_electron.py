import urllib.request
import zipfile
import os
import sys

url = "https://github.com/electron/electron/releases/download/v28.3.3/electron-v28.3.3-win32-x64.zip"
dest = "electron_binary.zip"
extract_path = "node_modules/electron/dist"

print(f"Downloading Electron from {url}...")
try:
    urllib.request.urlretrieve(url, dest)
    print("Download complete.")
    
    if not os.path.exists(extract_path):
        os.makedirs(extract_path)
        
    print(f"Extracting to {extract_path}...")
    with zipfile.ZipFile(dest, 'r') as zip_ref:
        zip_ref.extractall(extract_path)
    
    # Cleanup
    os.remove(dest)
    print("Extraction successful. Electron binary is ready.")
    
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
