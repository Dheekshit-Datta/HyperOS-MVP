import urllib.request
import zipfile
import os
import sys

url = "https://github.com/electron/electron/releases/download/v28.3.3/electron-v28.3.3-win32-x64.zip"
dest = "electron_binary.zip"
extract_path = "node_modules/electron/dist"



print(f"Checking for existing zip files...")
download_needed = True
valid_zip = None

# Check alternative names if the main one is locked
candidates = ["electron_new.zip", "electron_binary.zip"]

for candidate in candidates:
    if os.path.exists(candidate):
        print(f"Found {candidate}. Verifying...")
        try:
            with zipfile.ZipFile(candidate, 'r') as zip_ref:
                if zip_ref.testzip() is None:
                    print(f"Valid zip found: {candidate}")
                    valid_zip = candidate
                    download_needed = False
                    break
        except Exception:
            print(f"{candidate} appears corrupt or inaccessible.")

if valid_zip:
    dest = valid_zip
else:
    # If we have to download, try to write to a new name if the default is locked
    try:
        f = open(dest, 'a')
        f.close()
    except PermissionError:
        print(f"Default file {dest} is locked. switching to electron_new.zip")
        dest = "electron_new.zip"

if download_needed:
    print(f"Downloading Electron from {url} to {dest}...")

    try:
        import ssl
        ssl._create_default_https_context = ssl._create_unverified_context
        urllib.request.urlretrieve(url, dest)
        print("Download complete.")
    except Exception as e:
        print(f"Download failed: {e}")
        print("Please manually download the file from the URL above and save it as 'electron_binary.zip' in this folder.")
        sys.exit(1)

try:
    if not os.path.exists(extract_path):
        os.makedirs(extract_path)
        
    print(f"Extracting to {extract_path}...")
    with zipfile.ZipFile(dest, 'r') as zip_ref:
        zip_ref.extractall(extract_path)
    
    # Optional: cleanup only if we downloaded it? 
    # Let's keep the file for now so we don't have to re-download if extraction fails later.
    # os.remove(dest) 
    print("Extraction successful. Electron binary is ready.")
    
except Exception as e:
    print(f"Error during extraction: {e}")
    sys.exit(1)
