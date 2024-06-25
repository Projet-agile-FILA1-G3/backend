from flask import request, jsonify, Flask
from flask_cors import CORS

from api.service import find_most_relevant_items

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
