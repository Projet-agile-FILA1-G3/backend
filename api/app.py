import os

from dotenv import load_dotenv
from flask import Flask, request, jsonify
from sqlalchemy import func, desc

from models.models import Token, Item
from shared import string_utils
from shared.db import get_session

app = Flask(__name__)

load_dotenv('.env')


def find_most_relevant_items(words, limit=10):
    session = get_session()
    subquery = session.query(
        Token.item_id,
        func.sum(Token.rank).label('total_rank')
    ).filter(
        Token.word.in_(words)
    ).group_by(
        Token.item_id
    ).subquery()

    query = session.query(
        Item
    ).join(
        subquery, Item.id == subquery.c.item_id
    ).order_by(
        desc(subquery.c.total_rank)
    ).limit(limit)

    most_relevant_items = query.all()

    return most_relevant_items


@app.route('/search')
def search():
    words_string = request.args.get('words', '')
    words_string = string_utils.ProcessingString().process_text(words_string)
    print(words_string)
    words = words_string.split(' ')
    limit = int(request.args.get('limit', 10))

    if not words:
        return jsonify({"error": "No words provided"}), 400

    most_relevant_items = find_most_relevant_items(words, limit)

    if not most_relevant_items:
        return jsonify({"message": "No relevant items found"}), 404

    results = [{
        'id': str(item.id),
        'title': item.title,
        'description': item.description,
        'link': item.link,
        'pub_date': item.pub_date.isoformat(),
        'rss_id': str(item.rss_id)
    } for item in most_relevant_items]

    return jsonify(results), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
