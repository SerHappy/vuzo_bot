from sqlalchemy import Column, Integer, ForeignKey

from models.db import Base

# association_table = Table(
#     "user_subject",
#     Base.metadata,
#     Column("user_id", Integer, ForeignKey("user.id")),
#     Column("subject_id", Integer, ForeignKey("subject.id")),
# )


class EgePointsScore(Base):
    __tablename__ = "ege_points_score"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    subject_id = Column(Integer, ForeignKey("subject.id"))
    score = Column(Integer, nullable=False)

    def __init__(self, user_id: int, subject_id: int, score: int) -> None:
        self.user_id = user_id
        self.subject_id = subject_id
        self.score = score

    def __repr__(self) -> str:
        return f"Баллы за егэ [Пользователь:{self.user_id}, Предмет: {self.subject_id}, Баллы:{self.score}]"
