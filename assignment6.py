import requests
import os
from urllib.parse import urlparse
import hashlib
import time

def get_file_hash(content):
    return hashlib.sha256(content).hexdigest()

def main():
    print("Welcome to the Ubuntu Image Fetcher")
    print("A tool for mindfully collecting images from the web\n")
    
    # Get multiple URLs from user
    urls = input("Please enter image URLs (separated by spaces): ").strip().split()
    
    # Create directory if it doesn't exist
    os.makedirs("Fetched_Images", exist_ok=True)
    
    downloaded_hashes = set()
    
    for url in urls:
        try:
            print(f"\nFetching: {url}")
            response = requests.get(url, timeout=10, stream=True)
            response.raise_for_status()
            
            # Check important headers
            content_type = response.headers.get("Content-Type", "")
            if not content_type.startswith("image/"):
                print("✗ Skipped (not an image)")
                continue
            
            content_length = response.headers.get("Content-Length")
            if content_length and int(content_length) > 10 * 1024 * 1024:  # >10MB
                print("✗ Skipped (file too large)")
                continue
            
            # Read image content
            content = response.content
            file_hash = get_file_hash(content)
            
            # Prevent duplicate downloads
            if file_hash in downloaded_hashes:
                print("✗ Skipped (duplicate image)")
                continue
            downloaded_hashes.add(file_hash)
            
            # Extract filename from URL or generate one
            parsed_url = urlparse(url)
            filename = os.path.basename(parsed_url.path)
            
            if not filename:
                extension = content_type.split("/")[-1] or "jpg"
                filename = f"downloaded_image_{int(time.time())}.{extension}"
            
            # Avoid overwriting existing file
            filepath = os.path.join("Fetched_Images", filename)
            counter = 1
            while os.path.exists(filepath):
                name, ext = os.path.splitext(filename)
                filepath = os.path.join("Fetched_Images", f"{name}_{counter}{ext}")
                counter += 1
            
            # Save the image
            with open(filepath, "wb") as f:
                f.write(content)
            
            print(f"✓ Successfully fetched: {os.path.basename(filepath)}")
            print(f"✓ Image saved to {filepath}")
        
        except requests.exceptions.RequestException as e:
            print(f"✗ Connection error: {e}")
        except Exception as e:
            print(f"✗ An error occurred: {e}")
    
    print("\nAll URLs processed. Community enriched.")

if __name__ == "__main__":
    main()
