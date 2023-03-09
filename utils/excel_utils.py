import os
from data.directions.mirea_directions import get_mirea_directions
from db_utils import (
    get_User_ege_total_score,
    get_association_user_subject_all_records_by_id,
    get_subject_name_by_id,
)
import xlsxwriter
from decouple import config


def create_xlsx_directions(user_id) -> bool:
    find = False
    rowIndex = 2
    workbook = xlsxwriter.Workbook(
        os.path.join(
            config("PROJECT_DIR"), "data/parsing/mirea/Факультеты.xlsx"
        )
    )
    worksheet = workbook.add_worksheet("Факультеты")
    worksheet.write("A1", "Номер направления")
    worksheet.write("B1", "Название факультета")
    worksheet.write("C1", "Предметы для сдачи")
    worksheet.write(
        "D1",
        "Проходной балл",
    )
    worksheet.write("E1", "Количество бюджетных мест")
    worksheet.write("F1", "Стоимость обучения от")
    worksheet.write("G1", "Ссылка на страницу направления")

    directions = get_mirea_directions(1)
    print(directions)

    for direction in directions:
        direction_exams = eval(str(direction.exams))
        user_subjects = [
            subject
            for subject in get_association_user_subject_all_records_by_id(
                user_id
            )
        ]
        right_direction = True
        for priority, subjects in direction_exams.items():
            for subject in subjects:
                accept = False
                for user_subject in user_subjects:
                    print(user_subject[2])
                    print(subject, get_subject_name_by_id(user_subject[2]))
                    if subject == get_subject_name_by_id(user_subject[2]):
                        accept = True
                        break
                if accept:
                    break
                else:
                    right_direction = False
                    break
            if not right_direction:
                break
        if not right_direction:
            break
        try:
            threshold = int(direction.threshold)
        except (ValueError, TypeError):
            threshold = 0
        if (
            type(threshold) is int
            and get_User_ege_total_score(user_id) >= threshold
        ):
            find = True
            exams_chunk = []
            for priority, subjects in direction_exams.items():
                exams_chunk.append(", ".join(subjects))
            exams = " Или ".join(exams_chunk)
            worksheet.write(f"A{rowIndex}", direction.number)
            worksheet.write(f"B{rowIndex}", direction.name)
            worksheet.write(f"C{rowIndex}", exams)
            worksheet.write(
                f"D{rowIndex}",
                f"{'Нет данных' if threshold == 0 else direction.threshold}",
            )
            worksheet.write(
                f"E{rowIndex}",
                (
                    f"{'Нет данных' if direction.places_budget == None else direction.places_budget}"
                ),
            )
            worksheet.write(
                f"F{rowIndex}",
                (
                    f"{'Нет данных' if direction.lower_price == None else direction.lower_price}"
                ),
            )
            worksheet.write(
                f"G{rowIndex}",
                f"https://priem.mirea.ru/guide-direction?direction_id={direction.id}",
            )

            rowIndex += 1

    worksheet.set_column("A:G", 50)
    workbook.close()
    return True if find else False
