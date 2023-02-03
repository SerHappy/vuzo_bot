from sqlalchemy import Column, ForeignKey, String, Integer
from sqlalchemy.orm import relationship, mapped_column, Mapped

from models.db import Base, get_default_repr


class Rating(Base):
    __tablename__ = "rating"

    id = Column(Integer, primary_key=True)
    rating_name = mapped_column(String(250), unique=True, nullable=False)
    rating_item = relationship("RatingItem", back_populates="rating")

    def __init__(self, rating_name: Column[str]) -> None:
        self.rating_name = rating_name

    # def __str__(self) -> str:
    #     return f"<Рейтинг [Название: {self.rating_name}]>"
    def __str__(self) -> str:
        return get_default_repr(self.__table__.columns.keys())
