import uuid

import requests
from flask import jsonify

from shared.db import get_session
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
            return jsonify({"status": "Subscription validated"}), 200
        else:
            return jsonify({"error": "Subscription validation failed"}), 400

    elif hub_mode == "unsubscribe":
        subscription = session.query(Subscriptions).filter_by(hub_callback=hub_callback, hub_topic=hub_topic).first()
        if subscription:
            session.delete(subscription)
            session.commit()
            return jsonify({"status": "Unsubscribed successfully"}), 200
        else:
            return jsonify({"error": "Subscription not found"}), 404

    else:
        return jsonify({"error": "Invalid hub.mode"}), 400
