import uuid
from datetime import datetime
import logging
import config
import requests

from flask import request, jsonify, Flask, render_template
from flask_caching import Cache
from flask_cors import CORS
from api.websub_service import websub_treatment, notify_subscribers
from shared.models.Subscriptions import Subscriptions
from api.service import get_metrics_from_query, find_most_relevant_items, is_worker_alive, get_last_fetching_date, \
    get_number_of_articles, get_number_of_feed

config = {
    "CACHE_TYPE": "SimpleCache",
    "CACHE_DEFAULT_TIMEOUT": 300
}

app = Flask(__name__)
app.config.from_mapping(config)
cache = Cache(app)
CORS(app)


@app.route('/search')
@cache.cached(timeout=300, query_string=True)
def search():
    query_string = request.args.get('query', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    if not query_string:
        return jsonify({"error": "No query provided"}), 400

    most_relevant_items, total_items = find_most_relevant_items(query_string, page, per_page)

    if len(most_relevant_items) == 0:
        return jsonify({"message": "No relevant items found"}), 204

    results = [{
        'hashcode': str(item.hashcode),
        'title': item.title,
        'description': item.description,
        'link': item.link,
        'pub_date': item.pub_date.isoformat(),
        'feed_id': str(item.feed_id),
        'audio_link': item.audio_link,
        'image_link': item.image_link
    } for item in most_relevant_items]

    total_pages = (total_items + per_page - 1) // per_page

    return jsonify({
        'results': results,
        'total_items': total_items,
        'total_pages': total_pages
    }), 200


@app.route('/metrics')
def get_word_metrics():
    query = request.args.get('query', '')
    start_date_str = request.args.get('start_date', None)
    end_date_str = request.args.get('end_date', None)
    interval = request.args.get('interval', 'day').lower()

    if not query or not start_date_str or not end_date_str:
        return jsonify({"error": "Bad parameters"}), 400

    if interval not in ['hour', 'day', 'week']:
        return jsonify({"error": "Invalid interval parameter"}), 400

    metrics = get_metrics_from_query(query, datetime.fromisoformat(start_date_str), datetime.fromisoformat(end_date_str), interval)

    if len(metrics) == 0:
        return jsonify({"message": "No metrics found"}), 204

    return jsonify(metrics), 200


@app.route("/websub", methods=["GET", "POST"])
def websub_endpoint():
    if request.method == "GET":
        hub_mode = request.args.get("hub.mode")
        hub_challenge = request.args.get("hub.challenge")

        if hub_mode == "subscribe":
            return hub_challenge, 200
        else:
            return jsonify({"error": "Invalid Mode"}), 400

    else:
        hub_callback = request.form.get("hub.callback")
        hub_mode = request.form.get("hub.mode")
        hub_topic = request.form.get("hub.topic")
        hub_secret = request.form.get("hub.secret")
        hub_lease_seconds = request.form.get("hub.lease_seconds", 3600000)

        if not all([hub_callback, hub_mode, hub_topic]):
            return jsonify({"error": "Missing parameters"}), 400

        return websub_treatment(hub_callback, hub_mode, hub_topic, hub_secret, hub_lease_seconds)


@app.route('/notify', methods=['POST'])
def receive_feed_notification():
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({"error": "Invalid request, 'url' is required"}), 400

    feed_url = data['url']

    notify_subscribers(feed_url)
    logging.info(f"Notification sent successfully for feed: {feed_url}")

    return jsonify({"message": "Notification sent successfully"}), 200
  

@app.route('/healthcheck')
def healthcheck():
    return jsonify({
        "status": is_worker_alive() and "OK" or "DOWN",
        "last_fetching_date": get_last_fetching_date().isoformat(),
        "number_of_articles": get_number_of_articles(),
        "number_of_feeds": get_number_of_feed()
    })
