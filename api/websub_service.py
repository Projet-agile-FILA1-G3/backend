import logging
import uuid
from datetime import datetime, timedelta

import requests
from flask import jsonify

from shared.db import get_session
from shared.models.Feed import Feed
from shared.models.Item import Item
from shared.models.Subscriptions import Subscriptions

session = get_session()


def websub_treatment(hub_callback, hub_mode, hub_topic, hub_secret, hub_lease_seconds):
    if hub_mode == "subscribe":
        challenge = str(uuid.uuid4())
        response = requests.get(hub_callback,
                                params={"hub.mode": hub_mode, "hub.topic": hub_topic, "hub.challenge": challenge})
        if response.status_code == 200 and response.text == challenge:
            subscription = Subscriptions(
                hub_callback=hub_callback,
                hub_mode=hub_mode,
                hub_topic=hub_topic,
                hub_lease_seconds=hub_lease_seconds,
                hub_secret=hub_secret
            )
            session.add(subscription)
            session.commit()
            session.close()
            return jsonify({"status": "Subscription validated"}), 200
        else:
            return jsonify({"error": "Subscription validation failed"}), 400

    elif hub_mode == "unsubscribe":
        subscription = session.query(Subscriptions).filter_by(hub_callback=hub_callback, hub_topic=hub_topic).first()
        if subscription:
            session.delete(subscription)
            session.commit()
            session.close()
            return jsonify({"status": "Unsubscribed successfully"}), 200
        else:
            return jsonify({"error": "Subscription not found"}), 404

    else:
        return jsonify({"error": "Invalid hub.mode"}), 400


def notify_subscribers(feed_url):
    feed = session.query(Feed).filter_by(url=feed_url).first()
    if not feed:
        logging.info(f"Feed not found: {feed_url}")
        return {"error": "Feed not found"}

    items = session.query(Item).filter_by(feed_id=feed.id).all()
    subscriptions = session.query(Subscriptions).filter_by(hub_topic=feed_url).all()

    for subscription in subscriptions:
        expiration_date = subscription.subscription_date + timedelta(seconds=subscription.hub_lease_seconds)
        if expiration_date < datetime.now():
            session.delete(subscription)
            logging.info(f"Subscription expired: {subscription.id}")
            session.commit()
            continue
            
        for item in items:
            data = {
                "title": item.title,
                "description": item.description,
                "link": item.link,
                "pub_date": item.pub_date.isoformat()
            }
            headers = {
                "Content-Type": "application/json",
                "X-Hub-Signature": subscription.hub_secret
            }
            response = requests.post(subscription.hub_callback, json=data, headers=headers)
            if response.status_code != 200:
                logging.info(f"Failed to notify subscriber {subscription.hub_callback}")
