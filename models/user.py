from sqlalchemy import Column, String, Integer, Boolean
from sqlalchemy.orm import relationship
from models.db import Base


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    is_admin = Column(Boolean, default=False)
    telegram_id = Column(Integer, nullable=False)
    telegram_nickname = Column(String(250), nullable=False)
    score = relationship("EgePointsScore")

    def __init__(self, telegram_id: int, telegram_nickname: str) -> None:
        self.telegram_id = telegram_id
        self.telegram_nickname = telegram_nickname

    def __repr__(self) -> str:
        return f"Пользователь [Имя:{self.telegram_nickname}, id в Телеграме: {self.telegram_id}, Администратор:{self.is_admin}]"
