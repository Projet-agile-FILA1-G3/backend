from sqlalchemy import PrimaryKeyConstraint, Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from shared.models import Base


class Token(Base):
    __tablename__ = 'RR_TOKEN'
    word = Column(String, primary_key=True)
    rank = Column(Integer, nullable=False)
    item_id = Column(String, ForeignKey('RR_ITEM.hashcode'), primary_key=True)

    item = relationship("Item", back_populates="tokens")

    __table_args__ = (
        PrimaryKeyConstraint('word', 'item_id'),
    )

    def __init__(self, word, rank, item_id, **kw):
        super().__init__(**kw)
        self.word = word
        self.rank = rank
        self.item_id = item_id


def find_by_word(word: str):
    return Token.query.filter(Token.word == word).all()