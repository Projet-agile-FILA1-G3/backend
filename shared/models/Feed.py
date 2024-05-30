import uuid

from sqlalchemy import Column, UUID, String
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped

from shared.models import Base
from shared.models.Item import Item


class Feed(Base):
    __tablename__ = 'RR_FEED'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    url = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=False)
    title = Column(String, nullable=False)
    last_fetching_date = Column(String, nullable=False)

    items: Mapped[Item] = relationship(back_populates="feed", cascade="all, delete-orphan")

    def __init__(self, url, description, title, last_fetching_date, **kw: any):
        super().__init__(**kw)
        self.url = url
        self.description = description
        self.title = title
        self.last_fetching_date = last_fetching_date
