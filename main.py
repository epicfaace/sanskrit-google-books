# https://www.googleapis.com/books/v1/volumes?q=intitle:%22Prose%20english%20translation%22%20intitle:%22Mahabharata%22

import csv
import json
import os
import requests
import shutil

STORAGE_PATH = "dutt-mahabharata"
GOOGLE_BOOKS_RESULTS_PATH = os.path.join(STORAGE_PATH, "google-books-results.json")
DOWNLOAD_LINKS_PATH = os.path.join(STORAGE_PATH, "download-links.csv")

def clean_up():
    os.makedirs(STORAGE_PATH, exist_ok=True)
    shutil.rmtree(STORAGE_PATH)
    os.makedirs(STORAGE_PATH, exist_ok=True)

def scrape_google_books():
    """Scrapes Google Books to get the relevant books."""
    items = []
    offset = 0
    total_items = None
    while True:
        res = requests.get("https://www.googleapis.com/books/v1/volumes", params={
            "q": "intitle:'Prose english translation' intitle:Mahabharata",
            "maxResults": 40,
            "startIndex": offset
        }).json()
        if total_items is None:
            total_items = res["totalItems"]
        if "items" in res:
            items.extend(res["items"])
            offset += len(res["items"])
        else:
            break
    assert len(items) == total_items
    with open(GOOGLE_BOOKS_RESULTS_PATH, "w+") as f:
        json.dump(items, f, indent=2)

def create_download_links():
    """Reads the Google Books results to get a list of download links, then dumps that to a CSV file that
    can be manually accessed (as each link requires a CAPTCHA)."""
    with open(GOOGLE_BOOKS_RESULTS_PATH, "r") as f:
        items = json.load(f)

    with open(DOWNLOAD_LINKS_PATH, "w+") as f:
        fieldnames = ['title', 'subtitle', 'authors', 'publishedDate', 'industryIdentifiers', 'previewLink', 'publicDomain', 'pdfDownloadLink', 'epubDownloadLink']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for item in items:
            writer.writerow({
                'title': item['volumeInfo']['title'],
                'subtitle': item['volumeInfo'].get('subtitle', None),
                'authors': ','.join(item['volumeInfo'].get('authors', [])),
                'publishedDate': item['volumeInfo']['publishedDate'],
                'industryIdentifiers': ','.join(i['identifier'] for i in item['volumeInfo']['industryIdentifiers']),
                'previewLink': item['volumeInfo']['previewLink'],
                'publicDomain': item['accessInfo']['publicDomain'],
                'pdfDownloadLink': item['accessInfo']['pdf'].get('downloadLink', None),
                'epubDownloadLink': item['accessInfo']['epub'].get('downloadLink', None),
            })

if __name__ == '__main__':
    # clean_up()
    # scrape_google_books()
    create_download_links()