import os
import time
from datetime import datetime
from operator import or_

import pytz
from sqlalchemy import func, desc

from shared.db import get_session
from shared.models.Item import Item
from shared.models.Token import Token
from shared.persistence.FeedRepository import FeedRepository
from shared.persistence.ItemRepository import ItemRepository
from shared.persistence.TokenRepository import TokenRepository
from shared.tokenizer import get_tokens

session = get_session()
tokenRepository = TokenRepository(session)
feedRepository = FeedRepository(session)
itemRepository = ItemRepository(session)


def find_most_relevant_items(query, page=1, per_page=10):
    if not query:
        return [], 0

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

    count_subquery = session.query(func.count(subquery.c.item_id)).scalar()
    total_items = count_subquery if count_subquery is not None else 0

    date_weight = 1
    main_query = session.query(
        Item,
        (subquery.c.total_rank - func.log(date_weight * func.extract('epoch',
                                                                     current_date_no_tz - subquery.c.max_pub_date) / 86400)).label(
            'weighted_score')
    ).join(
        subquery, Item.hashcode == subquery.c.item_id
    ).order_by(
        desc('weighted_score')
    ).limit(per_page).offset((page - 1) * per_page)

    most_relevant_items = main_query.all()
    session.close()

    return [item for item, _ in most_relevant_items], total_items


def get_metrics_from_query(query, start_date, end_date, interval):
    if not query:
        return []

    words = get_tokens(query, 'fr')

    start_date_no_tz = start_date.replace(tzinfo=None)
    end_date_no_tz = end_date.replace(tzinfo=None)

    subqueries = [
        session.query(Token.item_id).filter(Token.word == word).distinct()
        for word in words
    ]

    item_ids_with_all_words = subqueries[0]
    for subquery in subqueries[1:]:
        item_ids_with_all_words = item_ids_with_all_words.intersect(subquery)

    query = session.query(
        func.date_trunc(interval, Item.pub_date).label('date'),
        func.count(Item.hashcode).label('count')
    ).filter(
        Item.hashcode.in_(item_ids_with_all_words),
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


def get_last_fetching_date():
    last_fetched_feed = feedRepository.find_last_fetched()
    last_fetched_feed_date = datetime.fromisoformat(last_fetched_feed.last_fetching_date)
    # transform the date to the timezone of europe/paris
    # add 2 hours to the date
    last_fetched_feed_date = last_fetched_feed_date.replace(tzinfo=pytz.utc)
    last_fetched_feed_date = last_fetched_feed_date.astimezone(pytz.timezone('Europe/Paris'))
    return last_fetched_feed_date


def is_worker_alive():
    last_fetched_date = get_last_fetching_date()
    if not last_fetched_date:
        return False
    diff = (datetime.now(pytz.timezone('Europe/Paris')) - last_fetched_date).total_seconds()
    return diff < float(os.getenv('SLEEPING_TIME', 1800))


def get_number_of_feed():
    return feedRepository.count()


def get_number_of_articles():
    return itemRepository.count()
