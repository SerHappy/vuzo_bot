from sqlalchemy import Boolean, Column, ForeignKey, String, Integer, Text
from sqlalchemy.orm import relationship
from models.db import Base


class UniversityDirection(Base):
    __tablename__ = "university_direction"

    id = Column(Integer, primary_key=True)
    university_id = Column(ForeignKey("university.id"), nullable=False)
    university = relationship("University", back_populates="university_directions")
    number = Column(String(8), nullable=False)
    is_aviable = Column(Boolean, nullable=False, default=True)
    name = Column(String(250), nullable=False)
    exams = Column(String(250), nullable=False)
    threshold = Column(Integer, default=0)
    description = Column(Text, nullable=True, default="No description")
    places_budget = Column(Integer, default=0)
    places_paid = Column(Integer, default=0)
    lower_price = Column(Integer, default=0)
    link = Column(String(250), nullable=True, default="No link")
    form = Column(String(250), nullable=False, default="Очная")
    location = Column(String(50), nullable=True, default="No information")

    def __init__(
        self,
        university_id,
        number,
        name,
        exams: list[str],
        is_aviable=True,
        threshold=0,
        description="No description",
        places_budget=0,
        places_paid=0,
        lower_price=0,
        link="No link",
        form="Очная",
        location="No information",
    ) -> None:
        self.university_id = university_id
        self.number = number
        self.is_aviable = is_aviable
        self.name = name
        self.exams = ",".join(exams)
        self.threshold = threshold
        self.description = description
        self.places_budget = places_budget
        self.places_paid = places_paid
        self.lower_price = lower_price
        self.link = link
        self.form = form
        self.location = location

    def __str__(self):
        string = f"Направление.\n"
        for attr in self.__table__.columns.keys():
            string += f"{attr=}\n"
