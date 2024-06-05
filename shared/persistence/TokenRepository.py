from sqlalchemy.orm import Session


class TokenRepository:

    def __init__(self, session: Session):
        self.session = session

    def store(self, token) -> None:
        self.session.add(token)
        self.session.commit()
