import math
import os
from datetime import datetime, timedelta

import pytz
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy import func, desc
from sqlalchemy.sql.operators import or_

from shared.models import Token, Item
from shared import string_utils
from shared.db import get_session

app = Flask(__name__)
CORS(app)

load_dotenv('.env')


def find_most_relevant_items(words, limit=10):
    session = get_session()

    if not words:
        return []

    like_conditions = [Token.word.ilike(f"%{word}%") for word in words]

    if len(like_conditions) == 1:
        conditions = like_conditions[0]
    else:
        conditions = or_(*like_conditions)

    current_date = datetime.now(pytz.timezone('Europe/Paris'))
    current_date_no_tz = current_date.replace(tzinfo=None)
    subquery = session.query(
        Token.item_id,
        func.sum(Token.rank).label('total_rank'),
        func.max(Item.pub_date).label('max_pub_date')
    ).filter(
        conditions
    ).join(
        Item, Token.item_id == Item.hashcode
    ).group_by(
        Token.item_id
    ).subquery()

    date_weight = 1
    query = session.query(
        Item,
        (subquery.c.total_rank - func.log(date_weight * func.extract('epoch',
                                                                     current_date_no_tz - subquery.c.max_pub_date) / 86400)).label(
            'weighted_score')
    ).join(
        subquery, Item.hashcode == subquery.c.item_id
    ).order_by(
        desc('weighted_score')
    ).limit(limit)

    most_relevant_items = query.all()
    session.close()

    return [item for item, _ in most_relevant_items]


@app.route('/search')
def search():
    query_string = request.args.get('query', '')

    if not query_string:
        return jsonify({"error": "No query provided"}), 400

    query_string = string_utils.ProcessingString().process_text(query_string)
    words = query_string.split(' ')
    limit = int(request.args.get('limit', 10))

    most_relevant_items = find_most_relevant_items(words, limit)

    if not most_relevant_items:
        return jsonify({"message": "No relevant items found"}), 204

    results = [{
        'hashcode': str(item.hashcode),
        'title': item.title,
        'description': item.description,
        'link': item.link,
        'pub_date': item.pub_date.isoformat(),
        'rss_id': str(item.rss_id)
    } for item in most_relevant_items]

    return jsonify(results), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
