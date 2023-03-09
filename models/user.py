from sqlalchemy import Column, String, Integer, Boolean
from sqlalchemy.orm import relationship
from models.db import Base, get_default_repr
from models.associaton_tables import association_user_subject


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    is_admin = Column(Boolean, default=False)
    telegram_id = Column(Integer, nullable=False)
    telegram_nickname = Column(String(250), nullable=False)
    ege_subjects_number = Column(Integer, default=0)
    ege_total_score = Column(Integer, default=0)
    ege_subjects = relationship(
        "Subject", secondary=association_user_subject, back_populates="users"
    )

    def __init__(self, telegram_id: int, telegram_nickname: str) -> None:
        self.telegram_id = telegram_id
        self.telegram_nickname = telegram_nickname

    def __str__(self) -> str:
        return get_default_repr(self.__table__.columns.keys())
