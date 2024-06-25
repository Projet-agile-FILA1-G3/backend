import uuid
from datetime import datetime
import logging
import config
import requests

from flask import request, jsonify, Flask, render_template
from flask_cors import CORS

from api.service import get_metrics_from_word, find_most_relevant_items
from api.websub_service import websub_treatment
from shared.models.Subscriptions import Subscriptions

app = Flask(__name__)
CORS(app)


@app.route('/search')
def search():
    query_string = request.args.get('query', '')

    if not query_string:
        return jsonify({"error": "No query provided"}), 400

    most_relevant_items = find_most_relevant_items(query_string)

    if len(most_relevant_items) == 0:
        return jsonify({"message": "No relevant items found"}), 204

    results = [{
        'hashcode': str(item.hashcode),
        'title': item.title,
        'description': item.description,
        'link': item.link,
        'pub_date': item.pub_date.isoformat(),
        'feed_id': str(item.feed_id)
    } for item in most_relevant_items]

    return jsonify(results), 200


@app.route('/metrics')
def get_word_metrics():
    word = request.args.get('word', '')
    start_date_str = request.args.get('start_date', None)
    end_date_str = request.args.get('end_date', None)
    interval = request.args.get('interval', 'day').lower()

    if not word or not start_date_str or not end_date_str:
        return jsonify({"error": "Bad parameters"}), 400

    if interval not in ['hour', 'day', 'week']:
        return jsonify({"error": "Invalid interval parameter"}), 400

    metrics = get_metrics_from_word(word, datetime.fromisoformat(start_date_str), datetime.fromisoformat(end_date_str),
                                    interval)

    if len(metrics) == 0:
        return jsonify({"message": "No metrics found"}), 204

    return jsonify(metrics), 200


@app.route("/websub", methods=["GET", "POST"])
def websub_endpoint():
    if request.method == "POST":
        hub_callback = request.form.get("hub.callback")
        hub_mode = request.form.get("hub.mode")
        hub_topic = request.form.get("hub.topic")
        hub_secret = request.form.get("hub.secret")
        hub_lease_seconds = request.form.get("hub.lease_seconds", 3600000)

        if not all([hub_callback, hub_mode, hub_topic, hub_secret]):
            return jsonify({"error": "Missing parameters"}), 400

        return websub_treatment(hub_callback, hub_mode, hub_topic, hub_secret, hub_lease_seconds)

    return render_template("index.html", title="RSS Radar WebSub Endpoint")
