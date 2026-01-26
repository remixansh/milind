import json
import os
import urllib.request
import ssl
import time

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_JSON = os.path.join(BASE_DIR, 'download.json')
TEST_DIR = os.path.join(BASE_DIR, 'test')

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def download_files():
    # Ensure test directory exists
    if not os.path.exists(TEST_DIR):
        os.makedirs(TEST_DIR)
        print(f"Created directory: {TEST_DIR}")
    
    # Load download list
    if not os.path.exists(DOWNLOAD_JSON):
        print(f"Error: {DOWNLOAD_JSON} not found.")
        return

    with open(DOWNLOAD_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"Found {len(data)} files to download.")
    print("-" * 50)

    success_count = 0
    fail_count = 0

    for url, filename in data.items():
        # Clean inputs
        url = url.strip()
        filename = filename.strip()
        
        # Determine extension from URL if not in filename
        # Assuming URL points to a file like .../file.pdf
        path_ext = os.path.splitext(url.split('?')[0])[1] # Remove query params
        if not path_ext:
            path_ext = '.pdf' # Default to PDF if unknown
            
        full_filename = f"{filename}{path_ext}"
        destination = os.path.join(TEST_DIR, full_filename)

        # Skip if already exists
        if os.path.exists(destination):
            print(f"[SKIP] {full_filename} already exists.")
            success_count += 1
            continue

        print(f"Downloading {filename}...", end='', flush=True)
        
        try:
            # Set a user agent to avoid being blocked by some servers
            req = urllib.request.Request(
                url, 
                data=None, 
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
            )
            
            start_time = time.time()
            with urllib.request.urlopen(req, context=ctx) as response, open(destination, 'wb') as out_file:
                out_file.write(response.read())
            
            duration = time.time() - start_time
            print(f" DONE ({duration:.1f}s)")
            success_count += 1
            
        except Exception as e:
            print(f"\n[ERROR] Failed to download {url}")
            print(f"Reason: {e}")
            fail_count += 1

    print("-" * 50)
    print(f"Download complete.")
    print(f"Success: {success_count}")
    print(f"Failed: {fail_count}")

if __name__ == "__main__":
    download_files()
