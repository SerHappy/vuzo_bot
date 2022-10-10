from sqlalchemy import Column, String, Integer, ForeignKey

from models.db import Base


class RatingItem(Base):
    __tablename__ = "rating_item"

    id = Column(Integer, primary_key=True)
    university_name = Column(String(250), nullable=False)
    world_rank = Column(String(10))
    local_rank = Column(String(10))
    rating_id = Column(Integer, ForeignKey("rating.id"), nullable=False)

    def __init__(
        self, university_name: str, world_rank: int, local_rank: int, rating_id: int
    ) -> None:
        self.university_name = university_name
        self.world_rank = world_rank
        self.local_rank = local_rank
        self.rating_id = rating_id

    def __repr__(self) -> str:
        return f"Элемент рейтинга [Университет:{self.university_name}, Мировой рейтинг: {self.world_rank}, Локальный рейтинг:{self.local_rank}]"
