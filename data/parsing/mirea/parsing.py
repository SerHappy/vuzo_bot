from os.path import exists
import requests
import json
from decouple import config
from models.db import Session
import os
import xlsxwriter
from db_utils import get_association_user_subject_all_records_by_id, get_subject_name_by_id, get_User_ege_total_score


def create_xlsx_directions(user_id) -> bool:
    session = Session()
    load_all_directions()
    find = False
    rowIndex = 2
    workbook = xlsxwriter.Workbook(os.path.join(config("PROJECT_DIR"), f"data/parsing/mirea/Факультеты.xlsx"))
    worksheet = workbook.add_worksheet("Факультеты")
    worksheet.write(f"A1", "Номер направления")
    worksheet.write(f"B1", "Название факультета")
    worksheet.write(f"C1", "Предметы для сдачи")
    worksheet.write(
        f"D1",
        f"Проходной балл",
    )
    worksheet.write(f"E1", "Количество бюджетных мест")
    worksheet.write(f"F1", "Стоимость обучения от")
    worksheet.write(f"G1", "Ссылка на страницу направления")
    mirea_ids = get_ids()

    records_list = get_association_user_subject_all_records_by_id(user_id)
    subjects_list = []
    for record in records_list:
        subject_name = get_subject_name_by_id(session, record.subject_id)
        subjects_list.append(subject_name)

    user_total_score = get_User_ege_total_score(user_id)

    for direction_id in mirea_ids:
        direction_file = open(
            os.path.join(
                config("PROJECT_DIR"),
                f"data/parsing/mirea/directions/{direction_id}.json",
            )
        )
        direction = json.load(direction_file)
        exams = get_exams(direction["guide_exams"])

        if len(set(exams)) != 0 and set(exams).issubset(subjects_list):
            try:
                threshold = int(direction["last_year_threshold"])
            except (ValueError, TypeError):
                threshold = "Нет данных"
            if type(threshold) is int and user_total_score >= threshold:
                find = True
                unpacked_subjects = ", ".join(exams)
                worksheet.write(f"A{rowIndex}", direction["code"])
                worksheet.write(f"B{rowIndex}", direction["program"])
                worksheet.write(f"C{rowIndex}", unpacked_subjects)
                worksheet.write(
                    f"D{rowIndex}",
                    f"{'Нет данных' if threshold == 0 else direction['last_year_threshold']}",
                )
                worksheet.write(f"E{rowIndex}", f"{'Нет данных' if direction['places_budget'] == None else direction['places_budget']}",)
                worksheet.write(
                    f"F{rowIndex}",
                    f"{'Нет данных' if direction['price_special_discount'] == None else direction['price_special_discount']}",
                )
                worksheet.write(
                    f"G{rowIndex}", f"https://priem.mirea.ru/guide-direction?direction_id={direction['id']}"
                )

                rowIndex += 1
        direction_file.close()
    worksheet.set_column(f"A:G", 50)
    workbook.close()
    return True if find else False


def _is_url_valid(url) -> bool:
    return requests.get(url).status_code == 200


def _is_file_exists(filename) -> bool:
    return exists(filename)


def _create_ids_file(filename) -> None:
    url = "https://priem.mirea.ru/lk/api/directions/get/"
    if not _is_url_valid(url):
        print("Invalid url")
        exit()
    directions = requests.get(url).json()
    js = [direction.get("id") for direction in directions]
    with open(filename, "w") as file:
        json.dump(js, file, indent=4, ensure_ascii=False)


def get_ids() -> list:
    filename = os.path.join(config("PROJECT_DIR"), f"data/parsing/mirea/ids.json")
    if not _is_file_exists(filename):
        _create_ids_file(filename)
    with open(filename) as file:
        data = json.load(file)
        return data


def get_exams(direction_exams: list) -> list:
    exams = []
    for exam in direction_exams:
        exams.append(exam["title"])
    return exams


def load_all_directions():
    ids = get_ids()

    for id in ids:
        if exists(os.path.join(config("PROJECT_DIR"), f"data/parsing/mirea/directions/{id}.json")):
            continue

        direction = requests.get(f"https://priem.mirea.ru/lk/api/directions/get/{id}").json()
        with open(
            os.path.join(
                config("PROJECT_DIR"),
                f"data/parsing/mirea/directions/{direction['id']}.json",
            ),
            "w",
        ) as file:
            json.dump(direction, file, indent=4, ensure_ascii=False)
