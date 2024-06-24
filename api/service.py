from datetime import datetime
from operator import or_

import pytz
from sqlalchemy import func, desc

from shared.db import get_session
from shared.models.Item import Item
from shared.models.Token import Token
from shared.persistence.TokenRepository import TokenRepository
from shared.tokenizer import get_tokens, stem_word

session = get_session()
tokenRepository = TokenRepository(session)


def find_most_relevant_items(query, limit=10):
    if not query:
        return []

    words = get_tokens(query, 'fr')

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


def get_metrics_from_word(word, start_date, end_date, interval):
    if not word:
        return []

    word = stem_word(word, 'fr')

    start_date_no_tz = start_date.replace(tzinfo=None)
    end_date_no_tz = end_date.replace(tzinfo=None)

    query = session.query(
        func.date_trunc(interval, Item.pub_date).label('date'),
        func.count(Token.word).label('count')
    ).join(
        Item, Token.item_id == Item.hashcode
    ).filter(
        Token.word == word,
        Item.pub_date >= start_date_no_tz,
        Item.pub_date <= end_date_no_tz
    ).group_by(
        func.date_trunc(interval, Item.pub_date)
    ).order_by(
        func.date_trunc(interval, Item.pub_date)
    )

    metrics = query.all()
    session.close()

    result = [{'date': record.date.isoformat(), 'count': record.count} for record in metrics]

    return result

