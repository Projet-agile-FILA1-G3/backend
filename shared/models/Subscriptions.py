import uuid
from datetime import datetime

import pytz
from sqlalchemy import Column, UUID, String, DateTime
from sqlalchemy.orm import relationship, Mapped, session

from shared.models import Base


class Subscriptions(Base):
    __tablename__ = 'RR_SUBSCRIPTIONS'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    hub_callback = Column(String, nullable=False)
    hub_mode = Column(String, nullable=False)
    hub_topic = Column(String, nullable=False)
    hub_lease_seconds = Column(String, nullable=False)
    hub_secret = Column(String)
    subscription_date = Column(DateTime, default=datetime.now(pytz.timezone('Europe/Paris')))

    def __init__(self, hub_callback, hub_mode, hub_topic, hub_lease_seconds, hub_secret, **kw):
        super().__init__(**kw)
        self.hub_callback = hub_callback
        self.hub_mode = hub_mode
        self.hub_topic = hub_topic
        self.hub_lease_seconds = hub_lease_seconds
        self.hub_secret = hub_secret

