from models.db import create_db, Session
from models.ege_points_score import EgePointsScore
from models.user import User
from models.rating import Rating
from models.subject import Subject
from models.rating_item import RatingItem

from config.subjects import subjects
from config.ratings import (
    ratings_names,
    qs_world_university_rankings_2022,
    times_higher_education_world_university_rankings_2022,
)


def create_database():
    create_db()
    load_data(Session())


def load_data(session: Session):
    for subject in subjects:
        sb = Subject(subject)
        session.add(sb)
    for name in ratings_names:
        session.add(Rating(name))
    for item in qs_world_university_rankings_2022:
        session.add(RatingItem(item[0], item[1], item[2], 1))
    for item in times_higher_education_world_university_rankings_2022:
        session.add(RatingItem(item[0], item[1], item[2], 2))
    session.commit()
    session.close()
