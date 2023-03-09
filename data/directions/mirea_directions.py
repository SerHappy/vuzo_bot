import requests
from models.db import Session
from models.university_direction import UniversityDirection


def load_mirea_directions():
    """Load MIREA directions into database"""
    directions_ids = [
        direction.get("id")
        for direction in requests.get(
            "https://priem.mirea.ru/lk/api/directions/get/"
        ).json()
    ]
    session = Session()
    for id in directions_ids:
        direction = requests.get(
            f"https://priem.mirea.ru/lk/api/directions/get/{id}"
        ).json()
        # Add only bachelor's degree
        if "бакалавриат" not in direction["guide_education_level"]["name"]:
            continue
        exams = {}
        for exam in direction["guide_exams"]:
            exams.setdefault(exam["pivot"]["priority"], []).append(
                exam["title"]
            )
        session.add(
            UniversityDirection(
                university_id=1,
                number=direction["code"],
                name=direction["program"],
                level=direction["guide_education_level"]["name"],
                exams=str(exams),
                is_aviable=True,
                threshold=direction["last_year_threshold"],
                description=direction["description"],
                places_budget=direction["places_budget"],
                places_paid=direction["places_paid"],
                lower_price=direction["price_discount_20"],
                link=(
                    "https://priem.mirea.ru/guide-direction?"
                    f"direction_id={direction['id']}"
                ),
                form=direction["guide_education_form"]["name"].title(),
                location=direction["guide_education_location"]["name"],
            )
        )
        session.commit()
        if id > 10:
            break


def get_mirea_direction(id: int) -> UniversityDirection:
    """Get MIREA direction by id"""
    session = Session()
    return (
        session.query(UniversityDirection)
        .filter(UniversityDirection.id == id)
        .scalar()
    )


def get_mirea_directions(university_id: int) -> list[UniversityDirection]:
    """Get MIREA directions by university id"""
    session = Session()
    return (
        session.query(UniversityDirection)
        .filter(UniversityDirection.university_id == university_id)
        .all()
    )
