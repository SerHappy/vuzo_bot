from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from models.db import Base


class Subject(Base):
    __tablename__ = "subject"

    id = Column(Integer, primary_key=True)
    subject_name = Column(String(50), unique=True, nullable=False)
    score = relationship("EgePointsScore")

    def __init__(self, subject_name: str) -> None:
        self.subject_name = subject_name

    def __repr__(self) -> str:
        return f"Предмет [Название: {self.subject_name}]"
