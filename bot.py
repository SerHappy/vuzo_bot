import asyncio
import nest_asyncio
import copy
from aiogram import Bot, types, Dispatcher, executor
import sqlite3
import aiogram.utils.markdown as md
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage

# connection = sqlite3.connect("database.db")
# cursor = connection.cursor()

user_scores = {}
individual_achievements_value = 0
universities = [
    [
        "МИРЭА",
        [
            [
                "Прикладная математика и информатика",
                [
                    ["Русский язык", "Математика", "Информатика и ИКТ"],
                ],
                267,
                87,
                177600,
            ],
            [
                "Прикладная математика",
                [
                    ["Русский язык", "Математика", "Информатика и ИКТ"],
                ],
                259,
                30,
                177600,
            ],
            [
                "Статистика",
                [
                    ["Русский язык", "Математика", "Информатика и ИКТ"],
                ],
                243,
                30,
                160000,
            ],
            [
                "Химия",
                [
                    ["Русский язык", "Математика", "Химия"],
                ],
                223,
                75,
                192000,
            ],
            [
                "Нанотехнологии и микросистемная техника",
                [
                    ["Русский язык", "Математика", "Физика"],
                ],
                212,
                30,
                219200,
            ],
            [
                "Техносферная безопасность",
                [
                    ["Русский язык", "Математика", "Физика"],
                    ["Русский язык", "Математика", "Химия"],
                ],
                190,
                19,
                177600,
            ],
        ],
    ],
    [
        "ВШЭ",
        [
            [
                "Бизнес-информатика",
                [
                    ["Русский язык", "Математика", "Иностранный язык"],
                ],
                297,
                110,
                650000,
            ],
            [
                "Биология",
                [
                    ["Русский язык", "Биология", "Химия"],
                    ["Русский язык", "Биология", "Математика"],
                ],
                294,
                50,
                470000,
            ],
            [
                "География",
                [
                    ["Русский язык", "География", "Информатика и ИКТ"],
                    ["Русский язык", "География", "Математика"],
                ],
                277,
                40,
                450000,
            ],
            [
                "Государственное и муниципальное управление",
                [
                    [
                        "Математика",
                        "Русский язык",
                        "Обществознание",
                        "Иностранный язык",
                    ],
                ],
                363,
                75,
                480000,
            ],
            [
                "Дизайн",
                [
                    [
                        "Литература",
                        "Русский язык",
                        "Вступительные",
                    ],
                ],
                292,
                52,
                620000,
            ],
        ],
    ],
    [
        "МГУ",
        [
            [
                "Астрономия",
                [
                    ["Русский язык", "Математика", "Физика", "Вступительные"],
                ],
                329,
                20,
                435970,
            ],
            [
                "Биоинженерия и биоинформатика",
                [
                    [
                        "Русский язык",
                        "Математика",
                        "Химия",
                        "Биология",
                        "Вступительные",
                    ],
                ],
                476,
                35,
                441440,
            ],
            [
                "Журналистика",
                [
                    [
                        "Русский язык",
                        "Литература",
                        "История",
                        "Вступительные",
                    ],
                    [
                        "Русский язык",
                        "Литература",
                        "Иностранный язык",
                        "Вступительные",
                    ],
                ],
                362,
                170,
                246000,
            ],
        ],
    ],
]
subjects = [
    "Математика",
    "Физика",
    "Русский язык",
    "Иностранный язык",
    "Информатика и ИКТ",
    "География",
    "Литература",
    "Биология",
    "Обществознание",
    "История",
    "Химия",
    "Вступительные",
]
qs_world_university_rankings_2022 = [
    [
        "Московский государственный университет имени М.В. Ломоносова",
        78,
        1,
    ],
    [
        "Санкт-Петербургский государственный университет",
        242,
        2,
    ],
    [
        "Новосибирский национальный исследовательский государственный"
        "университет",
        246,
        3,
    ],
    [
        "Национальный исследовательский Томский государственный университет",
        272,
        4,
    ],
    [
        "Московский государственный технический университет им. Н.Э. Баумана (национальный исследовательский университет)",
        285,
        5,
    ],
]
times_higher_education_world_university_rankings_2022 = [
    [
        "Московский государственный университет имени М.В. Ломоносова",
        158,
        1,
    ],
    [
        "Московский физико-технический институт (национальный исследовательский университет)",
        "201-250",
        2,
    ],
    [
        "Национальный исследовательский университет «Высшая школа экономики»",
        "301-350",
        3,
    ],
    [
        "Санкт-Петербургский политехнический университет Петра Великого",
        "301-350",
        3,
    ],
    [
        "Санкт-Петербургский горный университет",
        "401-500",
        4,
    ],
]
menu_keyboard = (
    types.ReplyKeyboardMarkup(resize_keyboard=True)
    .add(types.KeyboardButton("Калькулятор баллов ЕГЭ 🧮"))
    .add(types.KeyboardButton("Рейтинг вузов 🔝"))
    .add(types.KeyboardButton("Тест на профориентацию ℹ️"))
)
reply_keyboard = (
    types.ReplyKeyboardMarkup(
        resize_keyboard=True,
    )
    .add(types.KeyboardButton("Заново"))
    .add(types.KeyboardButton("Главное меню"))
)
questions = [
    ["Ухаживать за животными.",
        "Обслуживать машины, приборы (следить, регулировать)"],
    ["Помогать больным людям, лечить их.",
        "Составлять таблицы, схемы, программы вычислительных машин."],
    ["Следить за качеством книжных иллюстраций, плакатов, художественных открыток, грампластинок.",
        "Следить за состоянием, развитием растений."],
    ["Обрабатывать материалы (дерево, ткань, пластмассу и т.д.).",
        "Доводить товары до потребителя (рекламировать, продавать)."],
    ["Обсуждать научно-популярные книги, статьи.",
        "Обсуждать художественные книги."],
    ["Выращивать молодняк животных какой-либо породы.",
     "Тренировать сверстников (или младших) в выполнении каких-либо действий (трудовых, учебных, спортивных)."],
    ["Копировать рисунки, изображения, настраивать музыкальные инструменты.",
     "Управлять каким-либо грузовым, подъёмным, транс¬ портным средством (подъёмным краном, машиной и т.п.)."],
    ["Сообщать, разъяснять людям нужные для них сведения в справочном бюро, во время экскурсии и т.д.",
     "Художественно оформлять выставки, витрины, участвовать в подготовке концертов, пьес и т.п."],
    ["Ремонтировать изделия, вещи (одежду, технику), жилище.",
     "Искать и исправлять ошибки в текстах, таблицах, рисунках."],
    ["Лечить животных.",
     "Выполнять расчёты, вычисления."],
    ["Выводить новые сорта растений.",
     "Конструировать новые виды промышленных изделий (машины, одежду, дома и т.д.)."],
    ["Разбирать споры, ссоры между людьми, убеждать, разъяснять, поощрять, наказывать.",
     "Разбираться в чертежах, схемах, таблицах (проверять, уточнять, приводить в порядок)."],
    ["Наблюдать, изучать работу кружков художественной самодеятельности.",
     "Наблюдать, изучать жизнь микробов."],
    ["Обслуживать, налаживать медицинские приборы и аппараты.",
     "Оказывать людям медицинскую помощь при ранениях, ушибах, ожогах и т.п."],
    ["Составлять точные описания, отчёты о наблюдаемых явлениях, событиях, измеряемых объектах и др.",
     "Художественно описывать, изображать события наблюдаемые или представляемые."],
    ["Делать лабораторные анализы в больнице.",
     "Принимать, осматривать больных, беседовать с ними, назначать лечение."],
    ["Красить или расписывать стены помещений, поверхность изделий.",
     "Осуществлять монтаж здания или сборку машин, приборов."],
    ["Организовывать культ походы людей в театры, музеи, на экскурсии, в туристические путешествия и т.п.",
     "Играть на сцене, принимать участие в концертах."],
    ["Изготовлять по чертежам детали, изделия (машины, одежду), строить здания.",
     "Заниматься черчением, копировать карты, чертежи."],
    ["Вести борьбу с болезнями растений, с вредителями леса, сада.",
     "Работать на машинах (пишущая машина, компьютер, телетайп, телефакс)."],
]
answers = {
    "Nature": 0,
    "Technics": 0,
    "Human": 0,
    "Sign System": 0,
    "Artistic Image": 0,
}


class SubjectScoreForm(StatesGroup):
    amount = State()
    subject = State()
    score = State()
    individual_achievements = State()
    search = State()


class RatingForm(StatesGroup):
    rating = State()


class TestForm(StatesGroup):
    answer1_wait = State()
    answer2_wait = State()
    answer3_wait = State()
    answer4_wait = State()
    answer5_wait = State()
    answer6_wait = State()
    answer7_wait = State()
    answer8_wait = State()
    answer9_wait = State()
    answer10_wait = State()
    answer11_wait = State()
    answer12_wait = State()
    answer13_wait = State()
    answer14_wait = State()
    answer15_wait = State()
    answer16_wait = State()
    answer17_wait = State()
    answer18_wait = State()
    answer19_wait = State()
    answer20_wait = State()
    result = State()


async def set_commands(bot: Bot) -> None:
    """Отображает команды бота в чате при вводе '/'"""
    commands = [
        types.BotCommand(command="/start",
                         description="Привественное сообщение"),
        types.BotCommand(command="/menu", description="Главное меню"),
        types.BotCommand(command="/ege", description="Калькулятор баллов ЕГЭ"),
        types.BotCommand(command="/rating", description="Рейтинг вузов"),
        types.BotCommand(
            command="/test", description="Тест на определение типа будущей профессии"
        ),
    ]
    await bot.set_my_commands(commands)


def auth(func):
    """Декоратор"""

    async def wrapper(message):
        if message["from"]["id"] != 420041096:
            return await message.reply("Access Denied", reply=False)
        return await func(message)

    return wrapper


@auth
async def send_welcome_message(message: types.Message) -> None:
    """Отправляет приветственное сообщение"""
    await message.answer(
        f"Привет, {message.from_user.first_name}!\nЯ буду твоим путеводителем в мир вузов.\nВиртуальный помощник ищет образовательные программы высших профессиональный учебных заведений и помогает тебе определиться с местом, где ты проведёшь ближайшие 4 года. Здесь ты найдёшь всю интересующую тебя информацию: от наличия общежитий до проходных баллов.\nПосмотри все мои команды, набрав /menu, или воспользуйся шаблонами ниже, и скорее бери курс на вуз!",
        reply_markup=menu_keyboard,
    )


async def main_menu(message: types.Message, state=FSMContext) -> None:
    """Позволяет пользователю отменить любое действие и вернуться в главное меню"""
    current_state = await state.get_state()
    if current_state is not None:
        await state.finish()
    await message.answer(
        "Команды бота:\n"
        "/start - привественное сообщение\n"
        "/menu - главное меню\n"
        "/ege - Калькулятор баллов ЕГЭ\n"
        "/rating - Рейтинг вузов\n"
        "/test - Тест на определение типа будущей профессии\n"
        "Так же можешь воспользоваться кнопками с шаблонами сообщений :)"
        "\nPS: Все команды прекращают текущее действие и начинают новое, так что буть осторожен при их использовании!",
        reply_markup=menu_keyboard,
    )


async def start_FSM_for_subject(message: types.Message, state=FSMContext) -> None:
    """Начало машины состояния для калькулятора ЕГЭ"""
    # cursor.execute(f"SELECT id FROM user WHERE user_id = {int(message.from_user.id)}")
    # user_id = cursor.fetchall()[0][0]
    # connection.execute("PRAGMA foreign_keys = ON")
    # cursor.execute("DELETE FROM subjects WHERE user_id = (?)", (user_id,))
    # connection.commit()
    user_scores.clear()
    current_state = await state.get_state()
    if current_state is not None:
        await state.finish()
    await SubjectScoreForm.amount.set()
    await message.answer(
        "Введи кол-во предметов, которые ты сдавал/ла:",
        reply_markup=types.ReplyKeyboardRemove(),
    )


async def process_amount_invalid(message: types.Message) -> None:
    """Если количество предметов введено неверно"""
    await message.answer(
        f"Количество предметов дожно быть в диапозоне от 3 до {len(subjects)}\nВведи корректные данные:"
    )


async def process_amount(message: types.Message, state=FSMContext) -> None:
    """Обрабатывает количество предметов и запрашивает ввод предмета"""
    async with state.proxy() as data:
        if await state.get_state() == "SubjectScoreForm:amount":
            data["amount"] = int(message.text)
    subject_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [
        *subjects,
        "Назад в меню 🔙",
    ]
    subject_keyboard.add(*buttons)
    await SubjectScoreForm.subject.set()
    await message.answer(
        "Выбери предмет, который ты сдавал:", reply_markup=subject_keyboard
    )


async def process_subject_invalid(message: types.Message) -> None:
    """Если предмет введен неверно"""
    return await message.reply("Неверный ввод предмета!\nВведи корректные данные:")


async def process_subject(message: types.Message, state=FSMContext) -> None:
    """Обрабатывает введеный предмет и запрашивает ввод баллов"""
    async with state.proxy() as data:
        data["subject"] = message.text
    await SubjectScoreForm.score.set()
    await message.answer(
        f"Теперь введи свои баллы за предмет {message.text}: ",
        reply_markup=types.ReplyKeyboardRemove(),
    )


async def process_score_invalid(message: types.Message) -> None:
    """Если баллы введены неверно"""
    return await message.reply(
        "Баллы должны быть в диапазоне от 0 до 100!\nВведи корректные данные:"
    )


async def process_score(message: types.Message, state=FSMContext) -> None:
    """Обрабатывает введенные баллы за предмет"""
    # получение баллов из хранилища и добавление их в лок. словарь с ключем subject
    async with state.proxy() as data:
        data["score"] = int(message.text)
    # cursor.execute(f"SELECT id FROM user WHERE user_id = {int(message.from_user.id)}")
    # user_id = cursor.fetchall()[0][0]
    # cursor.execute(
    #     "INSERT INTO subjects (name, score, user_id) VALUES (?, ?, ?)",
    #     (data["subject"], data["score"], user_id),
    # )
    # cursor.execute(f"SELECT MAX(id) FROM subjects")
    # subject_id = cursor.fetchall()[0][0]
    # cursor.execute(
    #     "INSERT INTO user_subjects (user_id, subject_id) VALUES (?, ?)",
    #     (user_id, subject_id),
    # )
    # connection.commit()
    user_scores[data["subject"]] = data["score"]
    if len(user_scores) < data["amount"]:
        await SubjectScoreForm.subject.set()
        await process_amount(message, state=state)
    else:
        keyboard = copy.deepcopy(reply_keyboard)
        if "Математика" in user_scores and "Русский язык" in user_scores:
            keyboard.add(types.KeyboardButton("Продолжить"))
            answer = f"Вы можете перейти к подбору факультетов!"
        else:
            await state.finish()
            answer = f"Вы должны добавить баллы за обязательные предметы (Математика и Русский язык)"
        await message.answer(answer, reply_markup=keyboard)


async def process_id_start(message: types.Message, state=FSMContext) -> None:
    """Запрашивает у пользователя ввод количества дополнительных баллов"""
    async with state.proxy() as data:
        data["amount"] = data["amount"]
    if (
        "Математика" in user_scores and "Русский язык" in user_scores and len(
            user_scores) == data["amount"]):
        await SubjectScoreForm.next()
        await message.answer(
            f"Введи кол-во доп. баллов (введи 0, если их нет): ",
            reply_markup=types.ReplyKeyboardRemove(),
        )
    else:
        await empty(message)


async def process_id_invalid(message: types.Message) -> None:
    """Если дополнительные баллы введены неверно"""
    return await message.reply(
        "Доп. баллы должны быть в диапазоне от 0 до 10!\nВведите корректные данные: "
    )


async def process_id(message: types.Message, state=FSMContext) -> None:
    """Обработывает дополнительные баллы"""
    async with state.proxy() as data:
        data["individual_achievements_value"] = int(message.text)
    # cursor.execute(
    #     "UPDATE user SET individual_achievements_value = (?) WHERE user_id = (?)",
    #     (
    #         data["individual_achievements_value"],
    #         message.from_user.id,
    #     ),
    # )
    # connection.commit()
    global individual_achievements_value
    individual_achievements_value = data["individual_achievements_value"]
    await state.finish()
    answer = f"Добавлено {individual_achievements_value} баллов!"
    await message.answer(answer)
    answer = f"Текущие введенные значения:\nКоличество предметов: {len(user_scores)}\n"
    total_score = 0
    for subject, score in user_scores.items():
        answer += f"Предмет '{subject}', баллов - {score}\n"
        total_score += score
    if individual_achievements_value > 0:
        answer += f"\nКоличество доп. баллов - {individual_achievements_value}"
    answer += f"\nОбщая сумма баллов равна: {total_score+individual_achievements_value}"
    keyboard = copy.deepcopy(reply_keyboard)
    keyboard.add(types.KeyboardButton("Подбор факультетов"))
    await SubjectScoreForm.search.set()
    await message.answer(answer, reply_markup=keyboard)


async def process_search_start(message: types.Message) -> None:
    """Отправка пользователю подходящих факультетов или сообщения об их отсутствии"""
    # cursor.execute(
    #     "SELECT subjects_list_id, speciality.id, speciality.name, subject_name FROM speciality_subjects_list INNER JOIN subjects_list_subjects ON subjects_list_subjects.subjects_list = speciality_subjects_list.subjects_list_id INNER JOIN subjects ON subjects.id = subjects_list_subjects.subjects_id INNER JOIN speciality ON speciality.id = speciality_subjects_list.speciality_id"
    # )
    # universities_db = cursor.fetchall()
    find = False
    for university in universities:
        university_name = university[0]
        for speciality in university[1]:
            speciality_name = speciality[0]
            speciality_subjects = []
            speciality_score = speciality[2]
            speciality_budget = speciality[3]
            speciality_price = speciality[4]
            for subjects in speciality[1]:
                speciality_subjects = subjects
                if set(speciality_subjects).issubset(list(user_scores)):
                    total_score = 0
                    for subject in speciality_subjects:
                        total_score += user_scores[subject]
                    total_score += individual_achievements_value
                    if total_score >= speciality[2]:
                        find = True
                        unpacked_subjects = ", ".join(speciality_subjects)
                        text = f"Нашел для тебя подходящий факультет:\nУчебное заведение: {university_name}\nНазвание факультета: {speciality_name}\nПредметы для сдачи: {unpacked_subjects}\nПроходной балл: {speciality_score}\nКоличество бюджетных мест: {speciality_budget}\nСтоимость обучения от: {speciality_price}"
    if not find:
        text = f"К сожалению, мне не удалось найти подходящие факультеты"
    await message.answer(text, reply_markup=reply_keyboard)


async def start_FSM_for_rating(message: types.Message, state=FSMContext) -> None:
    """Начало машины состояния для рейтингов вузов"""
    current_state = await state.get_state()
    if current_state is not None:
        await state.finish()
    await RatingForm.rating.set()
    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True, row_width=1
    )
    buttons = [
        "QS World University Rankings – 2022",
        "Times Higher Education World University Rankings – 2022",
    ]
    keyboard.add(*buttons)
    await message.answer(
        "Выбери, какой рейтинг хочешь посмотреть",
        reply_markup=keyboard,
    )


async def process_rating_invalid(message: types.Message) -> None:
    """Если название рейтинга введено неверно"""
    return await message.reply(
        "Такого рейтинга у меня нет :(\nВведи корректные данные: "
    )


async def process_rating(message: types.Message) -> None:
    """Обработывает рейтинг вузов"""
    rng = (
        qs_world_university_rankings_2022
        if message.text == "QS World University Rankings – 2022"
        else times_higher_education_world_university_rankings_2022
    )
    answer = f"Рейтинг {message.text}:\n"
    for rating in rng:
        university_name = rating[0]
        university_global = rating[1]
        university_local = rating[2]
        answer += f"\n\n{university_name} - {university_global} место в Мире, {university_local} место в России"
    await message.answer(
        answer,
        reply_markup=reply_keyboard,
    )


async def process_answers(message: types.Message, state=FSMContext) -> None:
    """Обрабатывает все ответы на тесты"""
    async with state.proxy() as data:
        data["number"] = data.setdefault("number", 0) + 1
    current_state = await state.get_state()
    if current_state is None:
        await TestForm.first()
    else:
        await TestForm.next()
    current_state = await state.get_state()
    if current_state == "TestForm:result":
        keyboard = copy.deepcopy(reply_keyboard)
        keyboard.add(types.KeyboardButton("Узнать"))
        answer = "Тест завершен!\nСкорее выбирай кнопку 'Узнать'"
        await message.answer(answer, reply_markup=keyboard)
    else:

        keyboard = types.ReplyKeyboardMarkup(
            resize_keyboard=True, row_width=1
        )
        buttons = [
            *questions[data["number"]-1]
        ]
        keyboard.add(*buttons)
        if current_state == "TestForm:answer1_wait":
            await message.answer(
                "Ответь на вопрос: «Мне нравится…»",
                reply_markup=keyboard,
            )
        else:
            await message.answer(
                "Принято!\nОтветь на вопрос: «Мне нравится…»",
                reply_markup=keyboard,
            )


async def start_FSM_for_test(message: types.Message, state=FSMContext) -> None:
    """Начало машины состояния для теста"""
    global answers
    answers = {
        "Nature": 0,
        "Technics": 0,
        "Human": 0,
        "Sign System": 0,
        "Artistic Image": 0,
    }
    current_state = await state.get_state()
    if current_state is not None:
        await state.finish()
    await message.answer(
        "Привет, это тест на профориентацию!\nТест состоит из 20 пар утверждений. Внимательно прочитав оба утверждения, выбери то, которое больше соответствует твоему желанию. Выбор нужно сделать в каждой паре утверждений!\nPS: Для ответов используй предложенные шаблоны сообщений",
        reply_markup=types.ReplyKeyboardRemove(),
    )
    await process_answers(message, state)


async def process_answer_1(message: types.Message, state=FSMContext) -> None:
    if message.text == questions[0][0]:
        answers["Nature"] += 1
    if message.text == questions[0][1]:
        answers["Technics"] += 1
    await process_answers(message, state)


async def process_answer_2(message: types.Message, state=FSMContext) -> None:
    if message.text == questions[1][0]:
        answers["Human"] += 1
    if message.text == questions[1][1]:
        answers["Sign System"] += 1
    await process_answers(message, state)


async def process_answer_3(message: types.Message, state=FSMContext) -> None:
    if message.text == questions[2][0]:
        answers["Artistic Image"] += 1
    if message.text == questions[2][1]:
        answers["Nature"] += 1
    await process_answers(message, state)


async def process_answer_4(message: types.Message, state=FSMContext) -> None:
    if message.text == questions[3][0]:
        answers["Technics"] += 1
    if message.text == questions[3][1]:
        answers["Human"] += 1
    await process_answers(message, state)


async def process_answer_5(message: types.Message, state=FSMContext) -> None:
    if message.text == questions[4][0]:
        answers["Sign System"] += 1
    if message.text == questions[4][1]:
        answers["Artistic Image"] += 1
    await process_answers(message, state)


async def process_answer_6(message: types.Message, state=FSMContext) -> None:
    if message.text == questions[5][0]:
        answers["Nature"] += 1
    if message.text == questions[5][1]:
        answers["Human"] += 1
    await process_answers(message, state)


async def process_answer_7(message: types.Message, state=FSMContext) -> None:
    if message.text == questions[6][0]:
        answers["Artistic Image"] += 1
    if message.text == questions[6][1]:
        answers["Technics"] += 1
    await process_answers(message, state)


async def process_answer_8(message: types.Message, state=FSMContext) -> None:
    if message.text == questions[7][0]:
        answers["Human"] += 1
    if message.text == questions[7][1]:
        answers["Artistic Image"] += 1
    await process_answers(message, state)


async def process_answer_9(message: types.Message, state=FSMContext) -> None:
    if message.text == questions[8][0]:
        answers["Technics"] += 1
    if message.text == questions[8][1]:
        answers["Sign System"] += 1
    await process_answers(message, state)


async def process_answer_10(message: types.Message, state=FSMContext) -> None:
    if message.text == questions[9][0]:
        answers["Nature"] += 1
    if message.text == questions[9][1]:
        answers["Sign System"] += 1
    await process_answers(message, state)


async def process_answer_11(message: types.Message, state=FSMContext) -> None:
    if message.text == questions[10][0]:
        answers["Nature"] += 1
    if message.text == questions[10][1]:
        answers["Technics"] += 1
    await process_answers(message, state)


async def process_answer_12(message: types.Message, state=FSMContext) -> None:
    if message.text == questions[11][0]:
        answers["Human"] += 1
    if message.text == questions[11][1]:
        answers["Sign System"] += 1
    await process_answers(message, state)


async def process_answer_13(message: types.Message, state=FSMContext) -> None:
    if message.text == questions[12][0]:
        answers["Artistic Image"] += 1
    if message.text == questions[12][1]:
        answers["Nature"] += 1
    await process_answers(message, state)


async def process_answer_14(message: types.Message, state=FSMContext) -> None:
    if message.text == questions[13][0]:
        answers["Technics"] += 1
    if message.text == questions[13][1]:
        answers["Human"] += 1
    await process_answers(message, state)


async def process_answer_15(message: types.Message, state=FSMContext) -> None:
    if message.text == questions[14][0]:
        answers["Sign System"] += 1
    if message.text == questions[14][1]:
        answers["Artistic Image"] += 1
    await process_answers(message, state)


async def process_answer_16(message: types.Message, state=FSMContext) -> None:
    if message.text == questions[15][0]:
        answers["Nature"] += 1
    if message.text == questions[15][1]:
        answers["Human"] += 1
    await process_answers(message, state)


async def process_answer_17(message: types.Message, state=FSMContext) -> None:
    if message.text == questions[16][0]:
        answers["Artistic Image"] += 1
    if message.text == questions[16][1]:
        answers["Technics"] += 1
    await process_answers(message, state)


async def process_answer_18(message: types.Message, state=FSMContext) -> None:
    if message.text == questions[17][0]:
        answers["Human"] += 1
    if message.text == questions[17][1]:
        answers["Artistic Image"] += 1
    await process_answers(message, state)


async def process_answer_19(message: types.Message, state=FSMContext) -> None:
    if message.text == questions[18][0]:
        answers["Technics"] += 1
    if message.text == questions[18][1]:
        answers["Sign System"] += 1
    await process_answers(message, state)


async def process_answer_20(message: types.Message, state=FSMContext) -> None:
    if message.text == questions[19][0]:
        answers["Nature"] += 1
    if message.text == questions[19][1]:
        answers["Sign System"] += 1
    await process_answers(message, state)


async def proccess_test_result(message: types.Message) -> None:
    answer = "Ваш результат:\n\n"
    answer += f"Человек — природа {int((answers['Nature'] * 100)/8)}%\nЧеловек — техника {int((answers['Technics'] * 100)/8)}%\nЧеловек — человек {int((answers['Human'] * 100)/8)}%\nЧеловек — знаковая система {int((answers['Sign System'] * 100)/8)}%\nЧеловек — художественный образ {int((answers['Artistic Image'] * 100)/8)}%"
    answer += "\n\nЧеловек — природа.\nСюда входят профессии, в которых человек имеет дело с различными явлениями неживой и живой природы, например биолог, географ, геолог, математик, физик, химик и другие профессии, относящиеся к разряду естественных наук."
    answer += "\n\nЧеловек — техника.\nВ эту группу профессий включены различные виды трудовой деятельности, в которых человек  имеет дело с техникой, её использованием или конструированием, например профессия инженера, оператора, машиниста, механизатора, сварщика и т.п."
    answer += "\n\nЧеловек — человек.\nСюда включены все виды профессий, предполагающих взаимодействие людей, например политика, религия, педагогика, психология, медицина, торговля, право."
    answer += "\n\nЧеловек — знаковая система.\nВ эту группу включены профессии, касающиеся создания, изучения и использования различных знаковых систем, например лингвистика, языки математического программирования, способы графического представления результатов наблюдений и т.п."
    answer += "\n\nЧеловек — художественный образ.\nЭта группа профессий представляет собой различные виды художественно-творческого труда, например литература, музыка, театр, изобразительное искусство."
    await message.answer(answer, reply_markup=reply_keyboard)


async def empty(message: types.Message) -> None:
    """Обрабатывает неотловленные команды/сообщения"""
    await message.answer(
        "Неизвестый текст.\nВведите /menu для просмотра всех команд бота"
    )


def register_all_handlers(dp: Dispatcher):
    """Регестрирует хендлеры для каждой функции"""
    dp.register_message_handler(
        send_welcome_message, commands=["start", "help"], state="*"
    )
    dp.register_message_handler(
        start_FSM_for_subject,
        commands="ege",
        state="*",
    )
    dp.register_message_handler(
        start_FSM_for_rating,
        commands="rating",
        state="*",
    )
    dp.register_message_handler(
        start_FSM_for_test,
        commands="test",
        state="*",
    )
    dp.register_message_handler(
        start_FSM_for_subject,
        lambda message: message.text in ["Калькулятор баллов ЕГЭ 🧮"],
        state="*",
    )
    dp.register_message_handler(
        main_menu,
        commands=["menu"],
        state="*",
    )
    dp.register_message_handler(
        main_menu,
        lambda message: message.text.lower()
        in ["главное меню", "меню", "назад в меню 🔙", "назад"],
        state="*",
    )
    dp.register_message_handler(
        start_FSM_for_subject,
        lambda message: message.text in ["Заново"],
        state=SubjectScoreForm.amount,
    )
    dp.register_message_handler(
        start_FSM_for_subject,
        lambda message: message.text in ["Заново"],
        state=SubjectScoreForm.subject,
    )
    dp.register_message_handler(
        start_FSM_for_subject,
        lambda message: message.text in ["Заново"],
        state=SubjectScoreForm.score,
    )
    dp.register_message_handler(
        start_FSM_for_subject,
        lambda message: message.text in ["Заново"],
        state=SubjectScoreForm.individual_achievements,
    )
    dp.register_message_handler(
        start_FSM_for_subject,
        lambda message: message.text in ["Заново"],
        state=SubjectScoreForm.search,
    )
    dp.register_message_handler(
        process_amount_invalid,
        lambda message: not message.text.isdigit() or (
            int(message.text) < 3 or int(message.text) > len(subjects)),
        state=SubjectScoreForm.amount,
    )
    dp.register_message_handler(
        process_amount,
        lambda message: int(message.text) in range(3, len(subjects) + 1),
        state=SubjectScoreForm.amount,
    )
    dp.register_message_handler(
        process_subject_invalid,
        lambda message: message.text not in subjects,
        state=SubjectScoreForm.subject,
    )
    dp.register_message_handler(
        process_subject,
        lambda message: message.text in subjects,
        state=SubjectScoreForm.subject,
    )
    dp.register_message_handler(
        process_score_invalid,
        lambda message: message.text != "Продолжить" and (
            not message.text.isdigit() or (int(message.text) < 0 or int(message.text) > 100)),
        state=SubjectScoreForm.score,
    )
    dp.register_message_handler(
        process_score,
        lambda message: message.text.isdigit(),
        state=SubjectScoreForm.score,
    )
    dp.register_message_handler(
        process_id_start,
        lambda message: message.text == "Продолжить",
        state=SubjectScoreForm.score,
    )
    dp.register_message_handler(
        process_id_invalid,
        lambda message: not message.text.isdigit() or (
            int(message.text) < 0 or int(message.text) > 10),
        state=SubjectScoreForm.individual_achievements,
    )
    dp.register_message_handler(
        process_id,
        lambda message: message.text.isdigit(),
        state=SubjectScoreForm.individual_achievements,
    )
    dp.register_message_handler(
        process_search_start,
        lambda message: message.text in ["Подбор факультетов"],
        state=SubjectScoreForm.search,
    )
    dp.register_message_handler(
        start_FSM_for_rating,
        lambda message: message.text in ["Рейтинг вузов 🔝"],
        state="*",
    )
    dp.register_message_handler(
        start_FSM_for_rating,
        lambda message: message.text in ["Заново"],
        state=RatingForm.rating,
    )
    dp.register_message_handler(
        process_rating_invalid,
        lambda message: message.text
        not in [
            "QS World University Rankings – 2022",
            "Times Higher Education World University Rankings – 2022",
        ],
        state=RatingForm.rating,
    )
    dp.register_message_handler(
        process_rating,
        lambda message: message.text
        in [
            "QS World University Rankings – 2022",
            "Times Higher Education World University Rankings – 2022",
        ],
        state=RatingForm.rating,
    )
    dp.register_message_handler(
        start_FSM_for_test,
        lambda message: message.text in ["Тест на профориентацию ℹ️"],
        state="*",
    )
    dp.register_message_handler(
        start_FSM_for_test,
        lambda message: message.text in ["Заново"],
        state=TestForm.result,
    )
    dp.register_message_handler(
        process_answer_1,
        lambda message: message.text in questions[0],
        state=TestForm.answer1_wait,
    )
    dp.register_message_handler(
        process_answer_2,
        lambda message: message.text in questions[1],
        state=TestForm.answer2_wait,
    )
    dp.register_message_handler(
        process_answer_3,
        lambda message: message.text in questions[2],
        state=TestForm.answer3_wait,
    )
    dp.register_message_handler(
        process_answer_4,
        lambda message: message.text in questions[3],
        state=TestForm.answer4_wait,
    )
    dp.register_message_handler(
        process_answer_5,
        lambda message: message.text in questions[4],
        state=TestForm.answer5_wait,
    )
    dp.register_message_handler(
        process_answer_6,
        lambda message: message.text in questions[5],
        state=TestForm.answer6_wait,
    )
    dp.register_message_handler(
        process_answer_7,
        lambda message: message.text in questions[6],
        state=TestForm.answer7_wait,
    )
    dp.register_message_handler(
        process_answer_8,
        lambda message: message.text in questions[7],
        state=TestForm.answer8_wait,
    )
    dp.register_message_handler(
        process_answer_9,
        lambda message: message.text in questions[8],
        state=TestForm.answer9_wait,
    )
    dp.register_message_handler(
        process_answer_10,
        lambda message: message.text in questions[9],
        state=TestForm.answer10_wait,
    )
    dp.register_message_handler(
        process_answer_11,
        lambda message: message.text in questions[10],
        state=TestForm.answer11_wait,
    )
    dp.register_message_handler(
        process_answer_12,
        lambda message: message.text in questions[11],
        state=TestForm.answer12_wait,
    )
    dp.register_message_handler(
        process_answer_13,
        lambda message: message.text in questions[12],
        state=TestForm.answer13_wait,
    )
    dp.register_message_handler(
        process_answer_14,
        lambda message: message.text in questions[13],
        state=TestForm.answer14_wait,
    )
    dp.register_message_handler(
        process_answer_15,
        lambda message: message.text in questions[14],
        state=TestForm.answer15_wait,
    )
    dp.register_message_handler(
        process_answer_16,
        lambda message: message.text in questions[15],
        state=TestForm.answer16_wait,
    )
    dp.register_message_handler(
        process_answer_17,
        lambda message: message.text in questions[16],
        state=TestForm.answer17_wait,
    )
    dp.register_message_handler(
        process_answer_18,
        lambda message: message.text in questions[17],
        state=TestForm.answer18_wait,
    )
    dp.register_message_handler(
        process_answer_19,
        lambda message: message.text in questions[18],
        state=TestForm.answer19_wait,
    )
    dp.register_message_handler(
        process_answer_20,
        lambda message: message.text in questions[19],
        state=TestForm.answer20_wait,
    )
    dp.register_message_handler(
        proccess_test_result,
        lambda message: message.text in "Узнать",
        state=TestForm.result,
    )
    dp.register_message_handler(empty, state="*")


async def main():
    """Главный метод программы. Запускает бота"""
    API_TOKEN = "TOKEN"
    storage = MemoryStorage()

    bot = Bot(token=API_TOKEN)
    dp = Dispatcher(bot, storage=storage)
    register_all_handlers(dp)
    await set_commands(bot)
    executor.start_polling(dp, skip_updates=True)
    # connection.close()


if __name__ == "__main__":
    nest_asyncio.apply()
    asyncio.run(main())
