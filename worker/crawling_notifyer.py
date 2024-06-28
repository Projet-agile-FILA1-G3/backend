import logging
import os

import requests


def notify_api(feed_url: str):
    api_url = os.getenv('API_URL') + '/notify'

    data = {
        "url": feed_url
    }

    response = requests.post(api_url, json=data, headers={"Content-Type": "application/json"})

    if response.status_code == 200:
        logging.info("Notification sent successfully to api")
    else:
        logging.error(f"Failed to notify API. Status code: {response.status_code}")
