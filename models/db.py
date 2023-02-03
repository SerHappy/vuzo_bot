from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from decouple import config

CONNECTION_URL = config("SQLite", cast=str)
engine = create_engine(CONNECTION_URL, echo=True)
Session = sessionmaker(bind=engine)
Base = declarative_base()


def create_db():
    """Создает необходимые таблицы"""
    Base.metadata.create_all(engine)


def get_default_repr(attrs):
    string = "< "
    for attr in attrs:
        string += f"{attr=}\n"
    return string + " >"
