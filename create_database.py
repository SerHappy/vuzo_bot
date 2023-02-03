from models.db import create_db, Session

from models.rating import Rating
from models.subject import Subject
from models.rating_item import RatingItem

from config.subjects import subjects
from config.ratings import (
    RATINGS_NAMES,
    QS_WORLD_UNIVERSITY_RANKINGS_2022,
    TIMES_HIGHER_EDUCATION_WORLD_UNIVERSITY_RANKINGS_2022,
)


def create_database():
    create_db()
    load_data(Session())


def load_data(session):
    for subject in subjects:
        sb = Subject(subject)
        session.add(sb)
    for name in RATINGS_NAMES:
        session.add(Rating(name))
    for item in QS_WORLD_UNIVERSITY_RANKINGS_2022:
        session.add(RatingItem(item[0], item[1], item[2], 1))
    for item in TIMES_HIGHER_EDUCATION_WORLD_UNIVERSITY_RANKINGS_2022:
        session.add(RatingItem(item[0], item[1], item[2], 2))
    session.commit()
    session.close()
