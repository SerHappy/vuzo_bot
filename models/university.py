from sqlalchemy import Column, String, Integer, Text
from sqlalchemy.orm import relationship
from models.db import Base, get_default_repr


class University(Base):
    __tablename__ = "university"

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    description = Column(Text, nullable=False)
    site = Column(String(250), nullable=False)
    university_directions = relationship(
        "UniversityDirection", back_populates="university"
    )

    def __init__(self, name, description, site):
        self.name = name
        self.description = description
        self.site = site

    def __str__(self) -> str:
        return get_default_repr(self.__table__.columns.keys())
