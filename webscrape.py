import requests
from bs4 import BeautifulSoup
import csv
import re

# URL to scrape
url = "https://sanfrancisco.granicus.com/player/clip/50330?view_id=10&redirect=true"

# Extract record ID from URL
match = re.search(r"/clip/(\d+)", url)
record_id = match.group(1) if match else ""

# Fetch the page content
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Find the section with id='index' and grab agenda items
index_section = soup.find("section", {"id": "index"})
agenda_items = index_section.find_all("div", class_="index-point")

# Open CSV for writing
with open("agendas.csv", "w", newline="", encoding="utf-8") as csvfile:
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
