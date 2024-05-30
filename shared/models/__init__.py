from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):

    def __init__(self, **kw):
        super().__init__(**kw)

    def __str__(self):
        return str(self.__dict__)
