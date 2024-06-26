from datetime import datetime

from flask import request, jsonify, Flask
from flask_cors import CORS

from api.service import get_metrics_from_query, find_most_relevant_items

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
        'feed_id': str(item.feed_id),
        'audio_link': item.audio_link
    } for item in most_relevant_items]

    return jsonify(results), 200


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


@app.route('/healthcheck')
def healthcheck():
    return jsonify({
        "status": is_worker_alive(),
        "last_fetching_date": get_last_fetching_date().isoformat(),
        "number_of_articles": get_number_of_articles(),
        "number_of_feeds": get_number_of_feed()
    })
