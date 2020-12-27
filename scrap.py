import json
import os
import requests
from datetime import datetime
from parsel import Selector
from pathlib import Path

ROOT_URL = "http://www.zongosound.com"


def fetch_event_pages():
    PAGE_NUMBERS = range(1, 22)

    PAGE_URL_TEMPLATE = ROOT_URL + "/?page={}"

    for page_number in PAGE_NUMBERS:
        page_url = PAGE_URL_TEMPLATE.format(page_number)
        response = requests.get(page_url)
        selector = Selector(text=response.text)
        event_paths = selector.css("p.event-permalink a::attr(href)").getall()
        for event_path in event_paths:
            event_url = ROOT_URL + event_path
            response = requests.get(event_url)
            destination_dir = event_path[1:]
            os.makedirs(destination_dir, exist_ok=True)
            destination_file_path = os.path.join(destination_dir, "raw_page.html")
            with open(destination_file_path, "w") as fp:
                print("Write", destination_file_path)
                fp.write(response.text)


def remove_description_p_tag(text):
    return text[29:-4]


def download(url, destination):
    response = requests.get(url)
    with open(destination, "wb") as fp:
        print("Write", destination)
        fp.write(response.content)


def extract_data_from_event_pages():
    for event_dir in Path("events").iterdir():
        raw_page_path = event_dir / "raw_page.html"
        date_string = raw_page_path.parent.name.split("_")[0]
        date = datetime.strptime(date_string, "%d-%m-%Y").date()
        with open(raw_page_path) as fp:
            selector = Selector(text=fp.read())
            title = selector.css("title::text").get().split(" - ")[1].strip()
            location = selector.css("p.event-location::text").get().strip()
            description_paragraphs = [remove_description_p_tag(p) for p in selector.css("p.event-description").getall()]

            data_file_path = event_dir / "data.json"
            with open(data_file_path, "w") as fp:
                print("Write", data_file_path)
                json.dump({
                    "date": str(date),
                    "location": location,
                    "description": description_paragraphs,
                    "title": title,
                }, fp)

            image_path = selector.css("a.thumbnail::attr(href)").get()
            image_url = ROOT_URL + image_path
            local_image_path = event_dir / "image.jpg"
            download(url=image_url, destination=local_image_path)

            thumbnail_path = selector.css("a.thumbnail img::attr(src)").get()
            thumbnail_url = ROOT_URL + thumbnail_path
            local_thumbnail_path = event_dir / "thumbnail.jpg"
            download(url=thumbnail_url, destination=local_thumbnail_path)


extract_data_from_event_pages()
