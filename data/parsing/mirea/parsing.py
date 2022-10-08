from os.path import exists
import requests
import json
from decouple import config
import os


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
    filename = "ids.json"
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
        if exists(
            os.path.join(
                config("PROJECT_DIR"), f"data/parsing/mirea/directions/{id}.json"
            )
        ):
            continue

        direction = requests.get(
            f"https://priem.mirea.ru/lk/api/directions/get/{id}"
        ).json()
        with open(
            os.path.join(
                config("PROJECT_DIR"),
                f"data/parsing/mirea/directions/{direction['id']}.json",
            ),
            "w",
        ) as file:
            json.dump(direction, file, indent=4, ensure_ascii=False)
