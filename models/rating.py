from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship

from models.db import Base


class Rating(Base):
    __tablename__ = "rating"

    id = Column(Integer, primary_key=True)
    rating_name = Column(String(250), unique=True, nullable=False)
    ranking_row = relationship("RatingItem")

    def __init__(self, rating_name: str) -> None:
        self.rating_name = rating_name

    def __repr__(self) -> str:
        return f"Рейтинг [Название: {self.rating_name}]"
