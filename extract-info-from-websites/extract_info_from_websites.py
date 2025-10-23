import os
import sys

import urllib.request
import urllib.parse

import json

import requests
from bs4 import BeautifulSoup

def save_data_in_json(scraped_url, external_links, downloaded_images):
    results = {
        scraped_url: {
            "external_links": list(external_links), 
            "downloaded_images": downloaded_images
        }
    }
    
    output_json = "scrape_results.json"
    
    data_to_write = {}
    try:
        with open(output_json, "r") as f:
            data_to_write = json.load(f)
    except (IOError, json.JSONDecodeError):
        data_to_write = {}
        
    data_to_write.update(results)

    with open(output_json, "w") as f:
        json.dump(data_to_write, f, indent=4)
        
    print(f"Results for {scraped_url} saved to {output_json}")

def scrape_website(target_url: str, download_folder: str):

    try:
        os.makedirs(download_folder, exist_ok = True)
    except OSError as e:
        print(f"Error: Could not create directory '{download_folder}'")
        return
    
    try:
        base_domain = urllib.parse.urlparse(target_url).netloc
    except ValueError as e:
        print(f"Error: Invalid URL provided. {e}")
        return
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    external_links = set()
    downloaded_images = []

    try:
        response = requests.get(target_url, headers = headers)
        response.raise_for_status() #if unsuccessful -> error
        
        soup = BeautifulSoup(response.text, "html.parser")
    except requests.RequestException as e:
        print(f"Error: Failed to fetch url: {target_url}. {e}")
        return
    
    for link_tag in soup.find_all('a', href = True):
        href = link_tag.get("href")
        if not href or href.startswith('#'):
            continue

        absolute_link = urllib.parse.urljoin(target_url, href)

        parsed_href = urllib.parse.urlparse(absolute_link)
        link_domain = parsed_href.netloc

        if link_domain and link_domain != base_domain and parsed_href.scheme in ['http', 'https']:
            external_links.add(absolute_link)

    image_counter = 0
    for img_tag in soup.find_all('img'):
        img_src = img_tag.get('src')

        if not img_src:
            continue
        
        if img_src.startswith('data:'):
            print(f"Skipping embedded data image.")
            continue

        absolute_img_url = urllib.parse.urljoin(target_url, img_src)
        
        try:
            filename = os.path.basename(urllib.parse.urlparse(absolute_img_url).path)

            if not filename:
                print(f"Skipping image with no filename: {absolute_img_url}")
                continue

            save_path = os.path.join(download_folder, filename)
            original_save_path = save_path
            while os.path.exists(save_path):
                image_counter += 1
                name, ext = os.path.splitext(os.path.basename(original_save_path))
                filename = f"{name}_{image_counter}{ext}"
                save_path = os.path.join(download_folder, filename)

            print(f"Downloading: {absolute_img_url}")
            urllib.request.urlretrieve(absolute_img_url, save_path)
            downloaded_images.append(os.path.basename(save_path))

        except Exception as e:
            print(f"Error: Failed to download {absolute_img_url}. {e}")
            return

    save_data_in_json(target_url, external_links, downloaded_images)

download_folder = sys.argv[1]

with open("targets_list.json", "r") as fin:
    json_data = json.load(fin)

targets_url = json_data.get("targets_list", [])

for target_url in targets_url:
    scrape_website(target_url, download_folder)

