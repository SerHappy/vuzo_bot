from bs4 import BeautifulSoup, Tag
from anti_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from models.db import Session
from models.university import University
from models.university_direction import UniversityDirection
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from time import sleep
from selenium.webdriver.firefox.options import Options

ua = UserAgent()
headers = {
    "User-Agent": ua.random,
    "Accept": "*/*",
}
profile = webdriver.FirefoxProfile()
profile.set_preference("general.useragent.override", ua.random)
firefoxOptions = webdriver.FirefoxOptions()
options = Options()
options.headless = True


def _load_page(url: str) -> BeautifulSoup | None:
    """
    Loads the page and returns the HTML
    """
    driver = webdriver.Firefox(options=options)
    success = False
    while success is not True:
        try:
            driver.get(url)
            success = True
        except Exception as e:
            print(repr(e))
            sleep(2)
    delay = 10
    success = False
    while success is not True:
        try:
            WebDriverWait(driver, delay).until(
                EC.presence_of_element_located((By.ID, "hideForm"))
            )
            print(f"Page {url} is ready!")
            success = True
        except TimeoutException:
            print("Loading took too much time!")
    page = driver.execute_script("return document.body.innerHTML")
    driver.quit()
    return BeautifulSoup("".join(page), "lxml")


def _get_pages_count(url):
    """
    Returns the number of pages in the given url
    """
    return int(
        _load_page(url)
        .find("div", class_="invite fetcher")
        .find_all("a")[-2]
        .text
    )


def load_university_to_db(name, desc, url):
    session = Session()
    university = University(name, desc, url)
    session.add(university)
    session.commit()
    session.close()


def load_direction_to_db(
    university_name,
    number,
    name,
    level,
    exams,
    is_aviable,
    threshold,
    description,
    places_budget,
    places_paid,
    lower_price,
    link,
    form,
    location,
):
    session = Session()
    university_id = (
        session.query(University)
        .filter(University.name == university_name)
        .first()
        .id
    )

    university_direction = UniversityDirection(
        university_id,
        number,
        name,
        level,
        str(exams),
        is_aviable,
        threshold,
        description,
        places_budget,
        places_paid,
        lower_price,
        link,
        form,
        location,
    )
    session.add(university_direction)
    session.commit()
    session.close()


def get_data():
    main_url = "https://postupi.online/vuzi/"

    pages = _get_pages_count(main_url)

    for page in range(1, pages + 1):
        page_url = main_url + "?page_num=" + str(page)
        get_page_data(page_url)


def get_page_data(page_url):
    html_page = _load_page(page_url)

    universities = html_page.find_all("li", class_="list")

    for university in universities:
        get_university_card_data(university)


def get_university_card_data(university: Tag):
    university_name = university.find("h2", class_="list__h").find("a").text
    university_href = (
        university.find("h2", class_="list__h").find("a").get("href")
    )
    get_university_data(university_name, university_href)
    directions_href = (
        university.find("div", class_="dropdown-menu btn-ddown__menu")
        .find("a", string="Бакалавриат, специалитет")
        .get("href")
    )
    get_directios(directions_href, university_name)


def get_university_data(university_name, university_href):
    html_page = _load_page(university_href)
    name = university_name
    desc = html_page.find("div", class_="descr-min").text
    url = university_href
    load_university_to_db(name, desc, url)


def get_directios(url, university_name):
    try:
        directions_pages = _get_pages_count(url)
    except Exception as e:
        print(e)
        directions_pages = 1
    for directions_page in range(1, directions_pages + 1):
        directions_page_url = url + "?page_num=" + str(directions_page)
        directions_page_html = _load_page(directions_page_url)
        directions = directions_page_html.find_all("li", class_="list")
        for direcrion in directions:
            get_direction_card_data(direcrion, university_name)


def get_direction_card_data(direction, univesity_name):
    direction_name = direction.find("h2", class_="list__h").text
    direction_href = (
        direction.find("h2", class_="list__h").find("a").get("href")
    )
    try:
        direction_threshold = int(
            (
                direction.find("div", class_="list__score-wrap")
                .find("p")
                .find("span", class_="list__score-sm")
                .find("b")
                .text.strip()
            )
        )
    except Exception as e:
        print(repr(e), "direction_threshold not found")
        direction_threshold = 0
    scores = direction.find("div", class_="list__score-wrap").find_all("p")

    for score in scores:
        try:
            score.find("span", class_="visible-mid").text
        except Exception as e:
            print(repr(e), "score not found")
            continue
        if "Бюджетных мест" in score.find("span", class_="visible-mid").text:
            try:
                direction_places_budget = int(score.find("b").text.strip())
            except Exception as e:
                print(repr(e), "direction_places_budget not found")
                direction_places_budget = 0
        if "Платных мест" in score.find("span", class_="visible-mid").text:
            try:
                direction_places_paid = int(score.find("b").text.strip())
            except Exception as e:
                print(repr(e), "direction_places_paid not found")
                direction_places_paid = 0
    try:
        direction_lower_price = (
            (direction.find("span", class_="list__price").find("b").text)
            .replace("\xa0", "")
            .strip()
        )
    except Exception as e:
        print(repr(e), "direction_lower_price not found")
        direction_lower_price = 0

    get_direction_data(
        univesity_name,
        direction_name,
        direction_href,
        direction_threshold,
        direction_places_budget,
        direction_places_paid,
        direction_lower_price,
    )


def get_direction_data(
    univesity_name,
    direction_name,
    direction_href,
    direction_threshold,
    direction_places_budget,
    direction_places_paid,
    direction_lower_price,
):
    html_page = _load_page(direction_href)
    number = (
        html_page.find("p", class_="bg-nd__pre").find_all("a")[-1].get("href")
    ).split("/")[-2]
    name = direction_name
    details = html_page.find("div", class_="detail-box").find_all(
        "div", class_="detail-box__item"
    )
    for detail in details:
        if (
            detail.find("span", class_="detail-box__h")
            .text.replace("\xa0", "")
            .strip()
            == "Уровень образования"
        ):
            level = (
                detail.find("div")
                .find("span")
                .text.replace("\xa0", "")
                .strip()
            )
        if (
            detail.find("span", class_="detail-box__h")
            .text.replace("\xa0", "")
            .strip()
            == "Форма обучения"
        ):
            form = (
                detail.find("div")
                .find("a")
                .text.replace("\xa0", "")
                .replace(",", "")
                .strip()
            )
        if (
            detail.find("span", class_="detail-box__h")
            .text.replace("\xa0", "")
            .strip()
            == "Город"
        ):
            location = (
                detail.find("div").find("a").text.replace("\xa0", "").strip()
            )
    try:
        desc = (
            html_page.find("div", class_="descr-min descr-min_ellipsis")
            .find("p")
            .text
        )
    except AttributeError:
        desc = "Нет описания"
    try:
        exams_list = html_page.find(
            "div", class_="score-box swiper-slide 0"
        ).find_all("div", class_="score-box__item")
        exams_dict = dict()
        for priority, exam in enumerate(exams_list, start=1):
            exams_list = []
            exam_row = exam.find("div").find_all("p")
            for ex in exam_row:
                exams_list.append(
                    ex.text.replace("или", "").replace("\xa0", "").strip()
                )
            exams_dict[priority] = exams_list
    except Exception as e:
        print(repr(e))
        exams_dict = dict()
    is_aviable = True
    load_direction_to_db(
        university_name=univesity_name,
        number=number,
        name=name,
        level=level,
        exams=exams_dict,
        is_aviable=is_aviable,
        threshold=direction_threshold,
        description=desc,
        places_budget=direction_places_budget,
        places_paid=direction_places_paid,
        lower_price=direction_lower_price,
        link=direction_href,
        form=form,
        location=location,
    )
