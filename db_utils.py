from models.associaton_tables import association_user_subject
from models.subject import Subject
from models.user import User
from models.db import Session
from sqlalchemy import and_, desc


def add_user(telegram_id: int, username: str) -> None:
    session = Session()
    user_exists = _get_user(telegram_id)
    print("User exists: ", user_exists)
    if user_exists is None:
        user = User(telegram_id, username)
        session.add(user)
        session.commit()


def set_User_ege_subjects_number(
    telegram_id: int, subjects_number: int
) -> None:
    session = Session()
    session.query(User).filter(User.telegram_id == telegram_id).update(
        {"ege_subjects_number": subjects_number}
    )
    session.commit()


def set_User_ege_total_score(telegram_id, total_score):
    session = Session()
    session.query(User).filter(User.telegram_id == telegram_id).update(
        {"ege_total_score": total_score}
    )
    session.commit()


def get_User_ege_total_score(telegram_id):
    session = Session()
    return (
        session.query(User)
        .filter(User.telegram_id == telegram_id)
        .scalar()
        .ege_total_score
    )


def get_User_ege_subjects_number(telegram_id: int) -> int:
    session = Session()
    return (
        session.query(User)
        .filter(User.telegram_id == telegram_id)
        .scalar()
        .ege_subjects_number
    )


def get_association_user_subject_records_count_by_user_id(
    telegram_id: int,
) -> int:
    session = Session()
    return (
        session.query(association_user_subject)
        .filter(association_user_subject.columns.user_id == telegram_id)
        .count()
    )


def get_association_user_subject_all_records_by_id(telegram_id: int) -> list:
    session = Session()
    return (
        session.query(association_user_subject)
        .filter(
            and_(
                association_user_subject.columns.user_id == telegram_id,
                association_user_subject.columns.subject_id
                != _get_subject_id_by_name("Доп. баллы"),
            )
        )
        .all()
    )


def get_association_user_subject_indv_record(telegram_id: int):
    session = Session()
    return (
        session.query(association_user_subject)
        .filter(
            and_(
                association_user_subject.columns.user_id == telegram_id,
                association_user_subject.columns.subject_id
                == _get_subject_id_by_name("Доп. баллы"),
            )
        )
        .first()
    )


def set_association_user_subject_subject_id_by_user_id(
    telegram_id: int, subject: str
) -> None:
    session = Session()
    # subject_id = _get_subject_id_by_name(session, subject)
    # user_subject = association_user_subject(telegram_id, subject_id)
    # session.add(user_subject)
    statement = association_user_subject.insert().values(
        user_id=telegram_id, subject_id=_get_subject_id_by_name(subject)
    )
    session.execute(statement)
    session.commit()


def set_association_user_subject_score_by_desc_user_id(
    telegram_id: int, subject_id: int, score: int
) -> None:
    session = Session()
    session.query(association_user_subject).filter(
        and_(
            association_user_subject.columns.user_id == telegram_id,
            association_user_subject.columns.subject_id == subject_id,
        )
    ).update({"score": score})
    session.commit()


def get_association_user_subject_subject_id_by_user_id_desc(
    telegram_id: int,
) -> int:
    session = Session()
    row = (
        session.query(association_user_subject)
        .filter(
            association_user_subject.columns.user_id == telegram_id,
        )
        .order_by(desc(association_user_subject.columns.id))
        .first()
    )
    if row is None:
        raise Exception("No rows in association_user_subject")
    return row.subject_id


def set_association_user_subject_indv_score_for_user(
    telegram_id: int, indv_score: int
) -> None:
    session = Session()
    # indv_score_id = _get_subject_id_by_name(session, "Доп. баллы")
    # user_subject = association_user_subject(telegram_id, indv_score_id)
    # user_subject.score = indv_score
    # session.add(user_subject)
    # session.commit()
    statement = association_user_subject.insert().values(
        user_id=telegram_id,
        subject_id=_get_subject_id_by_name("Доп. баллы"),
        score=indv_score,
    )
    session.execute(statement)
    session.commit()


def _get_user(telegram_id) -> User:
    session = Session()
    return session.query(User).filter(User.telegram_id == telegram_id).scalar()


def _get_subject_id_by_name(subject) -> int:
    session = Session()
    return (
        session.query(Subject)
        .filter(Subject.subject_name == subject)
        .scalar()
        .id
    )


def get_subject_name_by_id(id) -> Subject:
    session = Session()
    return (
        session.query(Subject).filter(Subject.id == id).scalar().subject_name
    )


def delete_association_user_subject_records_by_user_id(telegram_id):
    session = Session()
    session.query(association_user_subject).filter(
        association_user_subject.columns.user_id == telegram_id
    ).delete()
    session.query(User).filter(User.telegram_id == telegram_id).update(
        {"ege_subjects_number": 0, "ege_total_score": 0}
    )
    session.commit()
