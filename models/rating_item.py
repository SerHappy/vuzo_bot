from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship, mapped_column
from models.db import Base, get_default_repr


class RatingItem(Base):
    __tablename__ = "rating_item"

    id = mapped_column(Integer, primary_key=True)
    university_name = mapped_column(String(250), nullable=False)
    world_rank = mapped_column(String(10))
    local_rank = mapped_column(String(10))
    rating_id = mapped_column(Integer, ForeignKey("rating.id"))
    rating = relationship("Rating", back_populates="rating_item")

    def __init__(
        self,
        university_name: Column[str],
        world_rank: Column[str],
        local_rank: Column[str],
        rating_id: Column[int],
    ) -> None:
        self.university_name = university_name
        self.world_rank = world_rank
        self.local_rank = local_rank
        self.rating_id = rating_id

    def __str__(self) -> str:
        return get_default_repr(self.__table__.columns.keys())
