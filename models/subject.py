from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from models.db import Base, get_default_repr
from models.associaton_tables import association_user_subject


class Subject(Base):
    __tablename__ = "subject"

    id = Column(Integer, primary_key=True)
    subject_name = Column(String(50), unique=True, nullable=False)
    users = relationship(
        "User",
        secondary=association_user_subject,
        back_populates="ege_subjects",
    )

    def __init__(self, subject_name: Column[str]) -> None:
        self.subject_name = subject_name

    def __str__(self) -> str:
        return get_default_repr(self.__table__.columns.keys())
