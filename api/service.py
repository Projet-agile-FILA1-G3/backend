from datetime import datetime
from operator import or_

import pytz
from sqlalchemy import func, desc

from shared.db import get_session
from shared.models.Item import Item
from shared.models.Token import Token
from shared.persistence.TokenRepository import TokenRepository
from shared.tokenizer import get_tokens

session = get_session()
tokenRepository = TokenRepository(session)


def find_most_relevant_items(query, limit=10):
    if not query:
        return []

    words = get_tokens(query)

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
