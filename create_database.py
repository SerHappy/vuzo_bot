from data.directions.mirea_directions import load_mirea_directions
from models.db import create_db, Session

from models.rating import Rating
from models.subject import Subject
from models.rating_item import RatingItem
from models.university import University

from config.subjects import subjects
from config.ratings import (
    RATINGS_NAMES,
    QS_WORLD_UNIVERSITY_RANKINGS_2022,
    TIMES_HIGHER_EDUCATION_WORLD_UNIVERSITY_RANKINGS_2022,
)


def create_database() -> None:
    """Create database with data"""
    create_db()
    load_data()


def load_data() -> None:
    """Load data into database"""
    session = Session()
    for subject in subjects:
        sb = Subject(subject)
        session.add(sb)
    for name in RATINGS_NAMES:
        session.add(Rating(name))
    for item in QS_WORLD_UNIVERSITY_RANKINGS_2022:
        session.add(RatingItem(item[0], item[1], item[2], 1))
    for item in TIMES_HIGHER_EDUCATION_WORLD_UNIVERSITY_RANKINGS_2022:
        session.add(RatingItem(item[0], item[1], item[2], 2))
    session.add(
        University(
            "РТУ МИРЭА",
            (
                "высшее учебное заведение в Москве, которое образовано в 2015"
                " году в результате объединения МИРЭА, МГУПИ, МИТХТ имени"
                " М. В. Ломоносова и ряда образовательных, научных,"
                " конструкторских и производственных организаций."
            ),
            "https://www.mirea.ru/",
        )
    )
    load_mirea_directions()
    session.commit()
    session.close()
