import uuid

from sqlalchemy import Column, UUID, String
from sqlalchemy.orm import relationship, Mapped, session

from shared.models import Base


class Feed(Base):
    __tablename__ = 'RR_FEED'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    url = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=False)
    title = Column(String, nullable=False)
    last_fetching_date = Column(String, nullable=False)
    lang = Column(String, nullable=True)

    items = relationship("Item", back_populates="feed", cascade="all, delete-orphan")

    def __init__(self, url, description, title, last_fetching_date, lang=None, **kw):
        super().__init__(**kw)
        self.url = url
        self.description = description
        self.title = title
        self.last_fetching_date = last_fetching_date
        self.lang = lang
