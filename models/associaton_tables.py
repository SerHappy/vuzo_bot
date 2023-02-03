from sqlalchemy import Column, Integer, ForeignKey, Table

from models.db import Base

association_user_subject: Table = Table(
    "user_subject",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey("user.id")),
    Column("subject_id", Integer, ForeignKey("subject.id")),
    Column("score", Integer, nullable=True, default=0),
)
