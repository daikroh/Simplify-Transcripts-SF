# webscrape.py
"""
This script scrapes the main page for records and a specific video page for agenda items.
It saves the scraped data into CSV files.
"""

import requests
from bs4 import BeautifulSoup
import csv
import re
from datetime import datetime


# Function to scrape the main page for records
def scrape_main_page(url, csv_filename="records.csv"):
    """Scrape the main page for records and save to CSV"""
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    rows = soup.select("table.sortable tbody tr")
    records = []

    for row in rows:
        tds = row.find_all("td")

        # First one is date, parse through it and remove the first ten characters to get the actual date
        date = tds[0].get_text(strip=True)[10:].strip()
        date = datetime.strptime(date, "%m/%d/%y").strftime("%Y-%m-%d 00:00:00")

        # Third one is video link, check if it exists
        video_link = tds[2].find("a")
        if not video_link or not video_link.has_attr("href"):
            continue
        href = video_link["href"]
        match = re.search(r"view_id=(\d+)&clip_id=(\d+)", href)

        # If we find a match, extract view_id and clip_id and append to records
        if match:
            view_id = match.group(1)
            clip_id = match.group(2)
            records.append([clip_id, view_id, date])

    # Open CSV for writing
    with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["record_id", "view_id", "published_date"])
        writer.writerows(records)


# Function to scrape a specific video page for agenda items
def scrape_video_page(url, csv_filename="agendas.csv"):
    """Scrape a video page for agenda items and save to CSV"""
    # Extract record ID from URL
    match = re.search(r"/clip/(\d+)", url)
    record_id = match.group(1) if match else ""

    # Fetch the page content
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # Find the section with id='index' and grab agenda items
    index_section = soup.find("section", {"id": "index"})
    agenda_items = index_section.find_all("div", class_="index-point")

    # Open CSV for writing
    with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["agenda_id", "record_id", "title", "start_time", "end_time"])

        for i, item in enumerate(agenda_items):
            agenda_id = item.get("data-uid")
            title = item.get_text(strip=True)
            start_time = item.get("time")

            # Determine end_time (time of next item)
            if i + 1 < len(agenda_items):
                end_time = agenda_items[i + 1].get("time")
            else:
                end_time = "999999"  # Arbitrary end time for the last item

            writer.writerow([agenda_id, record_id, title, start_time, end_time])


def main():
    scrape_main_page("https://sanfrancisco.granicus.com/ViewPublisher.php?view_id=10")
    scrape_video_page(
        "https://sanfrancisco.granicus.com/player/clip/50291?view_id=10&redirect=true"
    )
    print(">>> Scraping complete. Data saved to 'records.csv' and 'agendas.csv'.")


if __name__ == "__main__":
    main()
