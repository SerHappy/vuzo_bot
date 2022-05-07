import asyncio
import nest_asyncio
import copy
from aiogram import Bot, types, Dispatcher, executor
import aiogram.utils.markdown as md
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage

# Словорь результатов пользователя (предмет:балл)
user_scores = {}
# Баллы за индивидуальные достижения
individual_achievements_value = 0
# Список специальностей
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
# Список возможных предметов и ДВИ
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
# Список университетов в рейтинге QS World University Rankings – 2022
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
# Список университетов в рейтинге Times Higher Education World University Rankings – 2022
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
# Шаблоны сообщений с главными рубриками
menu_keyboard = (
    types.ReplyKeyboardMarkup(resize_keyboard=True)
    .add(types.KeyboardButton("Калькулятор баллов ЕГЭ 🧮"))
    .add(types.KeyboardButton("Рейтинги вузов 🔝"))
    .add(types.KeyboardButton("Тест на профориентацию ℹ️"))
)
# Шаблоны сообщений для возврата назад или в меню
reply_keyboard = (
    types.ReplyKeyboardMarkup(
        resize_keyboard=True,
    )
    .add(types.KeyboardButton("Заново"))
    .add(types.KeyboardButton("Главное меню"))
)
# Вопросы для теста
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
# Словарь результатов теста пользователя (Тип личности:кол-во баллов)
answers = {
    "Nature": 0,
    "Technics": 0,
    "Human": 0,
    "Sign System": 0,
    "Artistic Image": 0,
}


# Класс хранения состояний для рубрики "Калькулятор ЕГЭ"
class SubjectScoreForm(StatesGroup):
    amount = State()
    subject = State()
    score = State()
    individual_achievements = State()
    search = State()


# Класс хранения состояний для рубрики "Рейтинги вызов"
class RatingForm(StatesGroup):
    rating = State()


# Класс хранения состояний для рубрики "Тест на профориентацию"
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
    """Регистрация команд, отображаемых в интерфейсе Telegram"""
    commands = [
        types.BotCommand(command="/start",
                         description="Привественное сообщение"),
        types.BotCommand(command="/menu", description="Главное меню"),
        types.BotCommand(command="/ege", description="Калькулятор баллов ЕГЭ"),
        types.BotCommand(command="/rating", description="Рейтинги вузов"),
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


async def cancel_state(state=FSMContext):
    """Сбрасывает состояние и хранящиеся данные"""
    current_state = await state.get_state()
    if current_state is not None:
        await state.finish()


@auth
async def send_welcome_message(message: types.Message) -> None:
    """Отправляет приветственное сообщение"""
    # Формирование сообщения бота
    await message.answer(
        (f"Привет, {message.from_user.first_name}!\nЯ буду твоим "
         "путеводителем в мир вузов.\nВиртуальный помощник ищет "
         "образовательные программы высших профессиональный учебных "
         "заведений и помогает тебе определиться с местом, где ты проведёшь "
         "ближайшие 4 года. Здесь ты найдёшь всю интересующую тебя "
         "информацию: от наличия общежитий до проходных баллов.\n"
         "Посмотри все мои команды, набрав /menu, "
         "или воспользуйся шаблонами ниже, и скорее бери курс на вуз!"),
        reply_markup=menu_keyboard,
    )


async def main_menu(message: types.Message) -> None:
    """Прекращае любое состояние и показывает главное меню"""
    # Вызов функции сброса состояния
    cancel_state()
    # Формирование сообщения бота
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


async def start_FSM_for_subject(message: types.Message) -> None:
    """Начинает машину состояния для Калькулятора ЕГЭ"""
    # Сброс всех данных о предметах пользователя
    user_scores.clear()
    # Вызов функции сброса состояния
    cancel_state()
    # Установка состояния в "ожидание ввода кол-ва сданных предметов"
    await SubjectScoreForm.amount.set()
    # Формирование сообщения бота
    await message.answer(
        "Введи кол-во предметов, которые ты сдавал/ла:",
        reply_markup=types.ReplyKeyboardRemove(),
    )


async def process_amount_invalid(message: types.Message) -> None:
    """Сообщает об ошибке, если если количество предметов введено неверно"""
    # Формирование сообщения бота
    await message.answer(
        f"Количество предметов дожно быть в диапозоне от 3 до {len(subjects)}\nВведи корректные данные:"
    )


async def process_amount(message: types.Message, state=FSMContext) -> None:
    """Обрабатывает количество предметов и запрашивает ввод предмета"""
    async with state.proxy() as data:
        if await state.get_state() == "SubjectScoreForm:amount":
            # Запись в хранилище данных FSM по ключу amount кол-во предметов, если текущее состояние "ожидание ввода кол-ва предметов"
            data["amount"] = int(message.text)
    # Формирование шаблонов сообщений, содержащих все предметы, ДВИ и пункт 'Назад в меню'
    subject_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [
        *subjects,
        "Назад в меню 🔙",
    ]
    subject_keyboard.add(*buttons)
    # Установка состояния в "ожидание ввода предмета"
    await SubjectScoreForm.subject.set()
    # Формирование сообщения бота
    await message.answer(
        "Выбери предмет, который ты сдавал:", reply_markup=subject_keyboard
    )


async def process_subject_invalid(message: types.Message) -> None:
    """Сообщает об ошибке, если предмет введен неверно"""
    return await message.reply("Неверный ввод предмета!\nВведи корректные данные:")


async def process_subject(message: types.Message, state=FSMContext) -> None:
    """Обрабатывает введеный предмет и запрашивает ввод баллов"""
    async with state.proxy() as data:
        # Запись в хранилище данных FSM по ключу subject название предмета
        data["subject"] = message.text
    # Установка состояния в "ожидание ввода предмета"
    await SubjectScoreForm.score.set()
    # Формирование сообщения бота
    await message.answer(
        f"Теперь введи свои баллы за предмет {message.text}: ",
        reply_markup=types.ReplyKeyboardRemove(),
    )


async def process_score_invalid(message: types.Message) -> None:
    """Сообщает об ошибке, если баллы введены неверно"""
    # Формирование сообщения бота
    return await message.reply(
        "Баллы должны быть в диапазоне от 0 до 100!\nВведи корректные данные:"
    )


async def process_score(message: types.Message, state=FSMContext) -> None:
    """Обрабатывает введенные баллы за предмет и, либо выводит сообщение о продолжении, либо сообщает об ошибке и просит начать сначала"""
    async with state.proxy() as data:
        # Запись в хранилище данных FSM по ключу score количества баллов
        data["score"] = int(message.text)
    # Добавление в словарь user_scores пары (Название предмета:кол-во баллов)
    user_scores[data["subject"]] = data["score"]
    if len(user_scores) < data["amount"]:
        # Установка состояния в "ожидание ввода предмета,
        # если предметов введено меньше, чем число,
        # хранящиеся по ключу amount в хранилище данных FSM"
        await SubjectScoreForm.subject.set()
        # Вызов запрашивания ввода предмета
        await process_amount(message, state=state)
    else:
        # Формирование шаблонов сообщений путем глубокого копирования reply_keyboard
        keyboard = copy.deepcopy(reply_keyboard)
        if "Математика" in user_scores and "Русский язык" in user_scores:
            # Если пользователь ввел баллы за два обязательных предмета
            # (Математика и Русский языкы)
            # Добалвение еще одного шаблона
            keyboard.add(types.KeyboardButton("Продолжить"))
            #
            answer = f"Вы можете перейти к подбору факультетов!"
        else:
            # Вызов функции сброса состояния
            cancel_state()
            answer = f"Вы должны добавить баллы за обязательные предметы "
            "(Математика и Русский язык)"
        # Формирование сообщения бота
        await message.answer(answer, reply_markup=keyboard)


async def process_individual_archivments_start(message: types.Message, state=FSMContext) -> None:
    """Запрашивает у пользователя ввод количества дополнительных баллов"""
    # получение всех данных из хранилища данных FSM
    data = await state.get_data()
    if (
        "Математика" in user_scores and "Русский язык" in user_scores and
            len(user_scores) == data["amount"]):
        # Установка состояния "ожидание ввода кол-ва баллов за ИД",
        # если введены баллы за обязательные предметы и кол-во
        # введенных предметов равно data["amount"]
        await SubjectScoreForm.individual_achievements.set()
        # Формирование ответа
        await message.answer(
            f"Введи кол-во доп. баллов (введи 0, если их нет): ",
            reply_markup=types.ReplyKeyboardRemove(),
        )
    else:
        # Вызов метода обработки неизвестного текста
        await empty(message)


async def process_individual_archivments_invalid(message: types.Message) -> None:
    """Сообщает об ошибке, если дополнительные баллы введены неверно"""
    # Формирование сообщения бота
    return await message.reply(
        "Доп. баллы должны быть в диапазоне от 0 до 10!\nВведите корректные данные: "
    )


async def process_individual_archivments(message: types.Message, state=FSMContext) -> None:
    """Обработывает дополнительные баллы и выводит данные пользователя о сданных предметах и ИД"""
    async with state.proxy() as data:
        # Запись в хранилище данных FSM по ключу individual_achievements_value
        # количества баллов за ИД
        data["individual_achievements_value"] = int(message.text)
    global individual_achievements_value
    individual_achievements_value = data["individual_achievements_value"]
    # Вызов функции сброса состояния
    cancel_state()
    answer = f"Добавлено {individual_achievements_value} баллов!"
    # Формирование первого сообщения бота
    await message.answer(answer)
    answer = f"Текущие введенные значения:\nКоличество предметов: {len(user_scores)}\n"
    total_score = 0
    for subject, score in user_scores.items():
        # Добавление в переменную answer информации о предмете
        answer += f"Предмет '{subject}', баллов - {score}\n"
        # Прибавление к переменной общих баллов кол-ва баллов за предмет
        total_score += score
    if individual_achievements_value > 0:
        answer += f"\nКоличество доп. баллов - {individual_achievements_value}"
        # Прибавление к переменной общих баллов кол-ва баллов за ИД
        total_score += individual_achievements_value
    answer += f"\nОбщая сумма баллов равна: {total_score+individual_achievements_value}"
    # Формирование шаблонов сообщений путем глубокого копирования reply_keyboard
    keyboard = copy.deepcopy(reply_keyboard)
    # Добалвение еще одного шаблона
    keyboard.add(types.KeyboardButton("Подбор факультетов"))
    # Установка состояния в "ожидание ввода текста 'Подбор факультетов'"
    await SubjectScoreForm.search.set()
    # Формирование сообщения бота
    await message.answer(answer, reply_markup=keyboard)


async def process_search_start(message: types.Message) -> None:
    """Отправка пользователю подходящих факультетов или сообщения об их отсутствии"""
    # Переменная флаг. True - найден хотя бы 1 факультет, иначе False
    find = False
    # Проходимся по всем элементам в списке universities
    for university in universities:
        # Получение иммени университета
        university_name = university[0]
        # Проходимся по всем спецаильностям университета
        for speciality in university[1]:
            # Получение имени специальности
            speciality_name = speciality[0]
            # Получение баллов на бюджет
            speciality_score = speciality[2]
            # Получение бюджетых мест
            speciality_budget = speciality[3]
            # Получение цены за платное обучение
            speciality_price = speciality[4]
            # Проходимся по всем спискам предметов, необходимых для сдачи
            for subjects in speciality[1]:
                # Получение всех предметов из списка
                speciality_subjects = subjects
                # Если все предметы из списка сданы пользователем
                if set(speciality_subjects).issubset(list(user_scores)):
                    total_score = 0
                    for subject in speciality_subjects:
                        total_score += user_scores[subject]
                    # Считаем общее кол-во баллов за эти предметы
                    total_score += individual_achievements_value
                    if total_score >= speciality_score:
                        # Если их больше или они равные баллам для бюджета, то формируем текст с направлением
                        find = True
                        #
                        unpacked_subjects = ", ".join(speciality_subjects)
                        text = (f"Нашел для тебя подходящий факультет:\n"
                                f"Учебное заведение: {university_name}\n"
                                f"Название факультета: {speciality_name}\n"
                                f"Предметы для сдачи: {unpacked_subjects}\n"
                                f"Проходной балл: {speciality_score}\n"
                                f"Количество бюджетных мест: {speciality_budget}\n"
                                f"Стоимость обучения от: {speciality_price}")
    if not find:
        # Не найдено ни одно подходящее направление
        text = f"К сожалению, мне не удалось найти подходящие факультеты"
    # Формирование сообщения бота
    await message.answer(text, reply_markup=reply_keyboard)


async def start_FSM_for_rating(message: types.Message) -> None:
    """Начанает машину состояния для рейтингов вузов"""
    # Вызов функции сброса состояния
    cancel_state()
    # Установка состояния в "Ожидание ввода названия рейтинга"
    await RatingForm.rating.set()
    # Формирование шаблонов сообщений
    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True, row_width=1
    )
    buttons = [
        "QS World University Rankings – 2022",
        "Times Higher Education World University Rankings – 2022",
    ]
    keyboard.add(*buttons)
    # Формирование сообщения бота
    await message.answer(
        "Выбери, какой рейтинг хочешь посмотреть",
        reply_markup=keyboard,
    )


async def process_rating_invalid(message: types.Message) -> None:
    """Сообщает об ошибке, если название рейтинга введено неверно"""
    return await message.reply(
        "Такого рейтинга у меня нет :(\nВведи корректные данные: "
    )


async def process_rating(message: types.Message) -> None:
    """Обработывает название рейтинга вузов и выводит его"""
    # Проверка, какой рейтинг надо показать
    rating_to_show = (
        qs_world_university_rankings_2022
        if message.text == "QS World University Rankings – 2022"
        else times_higher_education_world_university_rankings_2022
    )
    answer = f"Рейтинг {message.text}:\n"
    # Проходимся по всем спискам рейтинга
    for rating in rating_to_show:
        # Получание имени вуза
        university_name = rating[0]
        # Получение места вуза в мире
        university_global = rating[1]
        # Получение места вуза в России
        university_local = rating[2]
        answer += f"\n\n{university_name} - {university_global} место в Мире, {university_local} место в России"
    # Формирование сообщения бота
    await message.answer(
        answer,
        reply_markup=reply_keyboard,
    )


async def process_answers(message: types.Message, state=FSMContext) -> None:
    """Обрабатывает ответ на тест и, либо запрашивает слудюущий ответ, либо сообщает о завершении теста"""
    async with state.proxy() as data:
        # Увеличение значения ключа number в хранилище данных FSM
        data["number"] = data.setdefault("number", 0) + 1
    # Получение текущего состояния
    current_state = await state.get_state()
    if current_state is None:
        # Установка состояния в первое состояние класса TestForm
        await TestForm.first()
    else:
        # Установка состояния в следующее состояние класса TestForm
        await TestForm.next()
    # Получение текущего состояния
    current_state = await state.get_state()
    if current_state == "TestForm:result":
        # Формирование завершения теста
        keyboard = copy.deepcopy(reply_keyboard)
        keyboard.add(types.KeyboardButton("Узнать"))
        answer = "Тест завершен!\nСкорее выбирай кнопку 'Узнать'"
        # Формирование сообщения бота
        await message.answer(answer, reply_markup=keyboard)
    else:
        # Формирование вопроса и пары ответов для теста
        keyboard = types.ReplyKeyboardMarkup(
            resize_keyboard=True, row_width=1
        )
        buttons = [
            *questions[data["number"]-1]
        ]
        keyboard.add(*buttons)
        if current_state == "TestForm:answer1_wait":
            # Текст ответа, если состояние "Ожидание первого ответа"
            answer = "Ответь на вопрос: «Мне нравится…»"
        else:
            answer = "Принято!\nОтветь на вопрос: «Мне нравится…»"
        # Формирование сообщения бота
        await message.answer(
            answer,
            reply_markup=keyboard,
        )


async def start_FSM_for_test(message: types.Message) -> None:
    """Начало машины состояния для теста"""
    # Сброс всех ответов  пользователя на тест
    global answers
    answers = {
        "Nature": 0,
        "Technics": 0,
        "Human": 0,
        "Sign System": 0,
        "Artistic Image": 0,
    }
    # Вызов функции сброса состояния
    cancel_state()
    # Формирование сообщения бота
    await message.answer(
        ("Привет, это тест на профориентацию!\n"
         "Тест состоит из 20 пар утверждений."
         "Внимательно прочитав оба утверждения, выбери то, "
         "которое больше соответствует твоему желанию."
         "Выбор нужно сделать в каждой паре утверждений!\n"
         "PS: Для ответов используй предложенные шаблоны сообщений"),
        reply_markup=types.ReplyKeyboardRemove(),
    )
    # Вызов функции для формирования первого вопроса
    await process_answers(message)


async def process_answer_1(message: types.Message, state=FSMContext) -> None:
    """Обработка ответа на вопрос 1 вызов функции для формирования следующего вопроса"""
    # Обработка ответа на вопрос
    if message.text == questions[0][0]:
        answers["Nature"] += 1
    if message.text == questions[0][1]:
        answers["Technics"] += 1
    # Вызов функции для формирования следующего вопроса
    await process_answers(message, state)


async def process_answer_2(message: types.Message, state=FSMContext) -> None:
    """Обработка ответа на вопрос 2 вызов функции для формирования следующего вопроса"""
    # Обработка ответа на вопрос
    if message.text == questions[1][0]:
        answers["Human"] += 1
    if message.text == questions[1][1]:
        answers["Sign System"] += 1
    # Вызов функции для формирования следующего вопроса
    await process_answers(message, state)


async def process_answer_3(message: types.Message, state=FSMContext) -> None:
    """Обработка ответа на вопрос 3 вызов функции для формирования следующего вопроса"""
    # Обработка ответа на вопрос
    if message.text == questions[2][0]:
        answers["Artistic Image"] += 1
    if message.text == questions[2][1]:
        answers["Nature"] += 1
    # Вызов функции для формирования следующего вопроса
    await process_answers(message, state)


async def process_answer_4(message: types.Message, state=FSMContext) -> None:
    """Обработка ответа на вопрос 4 вызов функции для формирования следующего вопроса"""
    # Обработка ответа на вопрос
    if message.text == questions[3][0]:
        answers["Technics"] += 1
    if message.text == questions[3][1]:
        answers["Human"] += 1
    # Вызов функции для формирования следующего вопроса
    await process_answers(message, state)


async def process_answer_5(message: types.Message, state=FSMContext) -> None:
    """Обработка ответа на вопрос 5 вызов функции для формирования следующего вопроса"""
    # Обработка ответа на вопрос
    if message.text == questions[4][0]:
        answers["Sign System"] += 1
    if message.text == questions[4][1]:
        answers["Artistic Image"] += 1
    # Вызов функции для формирования следующего вопроса
    await process_answers(message, state)


async def process_answer_6(message: types.Message, state=FSMContext) -> None:
    """Обработка ответа на вопрос 6 вызов функции для формирования следующего вопроса"""
    # Обработка ответа на вопрос
    if message.text == questions[5][0]:
        answers["Nature"] += 1
    if message.text == questions[5][1]:
        answers["Human"] += 1
    # Вызов функции для формирования следующего вопроса
    await process_answers(message, state)


async def process_answer_7(message: types.Message, state=FSMContext) -> None:
    """Обработка ответа на вопрос 7 вызов функции для формирования следующего вопроса"""
    # Обработка ответа на вопрос
    if message.text == questions[6][0]:
        answers["Artistic Image"] += 1
    if message.text == questions[6][1]:
        answers["Technics"] += 1
    # Вызов функции для формирования следующего вопроса
    await process_answers(message, state)


async def process_answer_8(message: types.Message, state=FSMContext) -> None:
    """Обработка ответа на вопрос 8 вызов функции для формирования следующего вопроса"""
    # Обработка ответа на вопрос
    if message.text == questions[7][0]:
        answers["Human"] += 1
    if message.text == questions[7][1]:
        answers["Artistic Image"] += 1
    # Вызов функции для формирования следующего вопроса
    await process_answers(message, state)


async def process_answer_9(message: types.Message, state=FSMContext) -> None:
    """Обработка ответа на вопрос 9 вызов функции для формирования следующего вопроса"""
    # Обработка ответа на вопрос
    if message.text == questions[8][0]:
        answers["Technics"] += 1
    if message.text == questions[8][1]:
        answers["Sign System"] += 1
    # Вызов функции для формирования следующего вопроса
    await process_answers(message, state)


async def process_answer_10(message: types.Message, state=FSMContext) -> None:
    """Обработка ответа на вопрос 10 вызов функции для формирования следующего вопроса"""
    # Обработка ответа на вопрос
    if message.text == questions[9][0]:
        answers["Nature"] += 1
    if message.text == questions[9][1]:
        answers["Sign System"] += 1
    # Вызов функции для формирования следующего вопроса
    await process_answers(message, state)


async def process_answer_11(message: types.Message, state=FSMContext) -> None:
    """Обработка ответа на вопрос 11 вызов функции для формирования следующего вопроса"""
    # Обработка ответа на вопрос
    if message.text == questions[10][0]:
        answers["Nature"] += 1
    if message.text == questions[10][1]:
        answers["Technics"] += 1
    # Вызов функции для формирования следующего вопроса
    await process_answers(message, state)


async def process_answer_12(message: types.Message, state=FSMContext) -> None:
    """Обработка ответа на вопрос 12 вызов функции для формирования следующего вопроса"""
    # Обработка ответа на вопрос
    if message.text == questions[11][0]:
        answers["Human"] += 1
    if message.text == questions[11][1]:
        answers["Sign System"] += 1
    # Вызов функции для формирования следующего вопроса
    await process_answers(message, state)


async def process_answer_13(message: types.Message, state=FSMContext) -> None:
    """Обработка ответа на вопрос 13 вызов функции для формирования следующего вопроса"""
    # Обработка ответа на вопрос
    if message.text == questions[12][0]:
        answers["Artistic Image"] += 1
    if message.text == questions[12][1]:
        answers["Nature"] += 1
    # Вызов функции для формирования следующего вопроса
    await process_answers(message, state)


async def process_answer_14(message: types.Message, state=FSMContext) -> None:
    """Обработка ответа на вопрос 14 вызов функции для формирования следующего вопроса"""
    # Обработка ответа на вопрос
    if message.text == questions[13][0]:
        answers["Technics"] += 1
    if message.text == questions[13][1]:
        answers["Human"] += 1
    # Вызов функции для формирования следующего вопроса
    await process_answers(message, state)


async def process_answer_15(message: types.Message, state=FSMContext) -> None:
    """Обработка ответа на вопрос 15 вызов функции для формирования следующего вопроса"""
    # Обработка ответа на вопрос
    if message.text == questions[14][0]:
        answers["Sign System"] += 1
    if message.text == questions[14][1]:
        answers["Artistic Image"] += 1
    # Вызов функции для формирования следующего вопроса
    await process_answers(message, state)


async def process_answer_16(message: types.Message, state=FSMContext) -> None:
    """Обработка ответа на вопрос 16 вызов функции для формирования следующего вопроса"""
    # Обработка ответа на вопрос
    if message.text == questions[15][0]:
        answers["Nature"] += 1
    if message.text == questions[15][1]:
        answers["Human"] += 1
    # Вызов функции для формирования следующего вопроса
    await process_answers(message, state)


async def process_answer_17(message: types.Message, state=FSMContext) -> None:
    """Обработка ответа на вопрос 17 вызов функции для формирования следующего вопроса"""
    # Обработка ответа на вопрос
    if message.text == questions[16][0]:
        answers["Artistic Image"] += 1
    if message.text == questions[16][1]:
        answers["Technics"] += 1
    # Вызов функции для формирования следующего вопроса
    await process_answers(message, state)


async def process_answer_18(message: types.Message, state=FSMContext) -> None:
    """Обработка ответа на вопрос 18 вызов функции для формирования следующего вопроса"""
    # Обработка ответа на вопрос
    if message.text == questions[17][0]:
        answers["Human"] += 1
    if message.text == questions[17][1]:
        answers["Artistic Image"] += 1
    # Вызов функции для формирования следующего вопроса
    await process_answers(message, state)


async def process_answer_19(message: types.Message, state=FSMContext) -> None:
    """Обработка ответа на вопрос 19 вызов функции для формирования следующего вопроса"""
    # Обработка ответа на вопрос
    if message.text == questions[18][0]:
        answers["Technics"] += 1
    if message.text == questions[18][1]:
        answers["Sign System"] += 1
    # Вызов функции для формирования следующего вопроса
    await process_answers(message, state)


async def process_answer_20(message: types.Message, state=FSMContext) -> None:
    """Обработка ответа на вопрос 20 вызов функции для вывода сообщения о завершении теста"""
    # Обработка ответа на вопрос
    if message.text == questions[19][0]:
        answers["Nature"] += 1
    if message.text == questions[19][1]:
        answers["Sign System"] += 1
    # Вызов функции для вывода сообщения о завершении теста
    await process_answers(message, state)


async def proccess_test_result(message: types.Message) -> None:
    """Выводит результаты теста"""
    # Формирование теста ответа бота
    answer = "Ваш результат:\n\n"
    answer += (f"Человек — природа {int((answers['Nature'] * 100)/8)}%\n"
               f"Человек — техника {int((answers['Technics'] * 100)/8)}%\n"
               f"Человек — человек {int((answers['Human'] * 100)/8)}%\n"
               f"Человек — знаковая система "
               f"{int((answers['Sign System'] * 100)/8)}%\n"
               f"Человек — художественный образ "
               f"{int((answers['Artistic Image'] * 100)/8)}%")
    answer += ("\n\nЧеловек — природа.\n"
               "Сюда входят профессии, в которых человек имеет дело "
               "с различными явлениями неживой и живой природы, "
               "например биолог, географ, геолог, "
               "математик, физик, химик и другие профессии, "
               "относящиеся к разряду естественных наук.")
    answer += ("\n\nЧеловек — техника.\n"
               "В эту группу профессий включены различные виды трудовой "
               "деятельности, в которых человек  имеет дело с техникой, "
               "её использованием или конструированием, например профессия "
               "инженера, оператора, машиниста, "
               "механизатора, сварщика и т.п.")
    answer += ("\n\nЧеловек — человек.\n"
               "Сюда включены все виды профессий, предполагающих "
               "взаимодействие людей, например политика, религия, "
               "педагогика, психология, медицина, торговля, право.")
    answer += ("\n\nЧеловек — знаковая система.\n"
               "В эту группу включены профессии, касающиеся создания, "
               "изучения и использования различных знаковых систем, "
               "например лингвистика, языки математического "
               "программирования, способы графического представления "
               "результатов наблюдений и т.п.")
    answer += ("\n\nЧеловек — художественный образ.\n"
               "Эта группа профессий представляет собой различные "
               "виды художественно-творческого труда, например литература, "
               "музыка, театр, изобразительное искусство.")
    # Формирование сообщения бота
    await message.answer(answer, reply_markup=reply_keyboard)


async def empty(message: types.Message) -> None:
    """Обрабатывает неотловленные команды/сообщения"""
    # Формирование сообщения бота
    await message.answer(
        "Неизвестый текст.\nВведите /menu для просмотра всех команд бота"
    )


def register_all_handlers(dp: Dispatcher):
    """Регестрирует хэндлеры для каждой функции"""
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
        process_individual_archivments_start,
        lambda message: message.text == "Продолжить",
        state=SubjectScoreForm.score,
    )
    dp.register_message_handler(
        process_individual_archivments_invalid,
        lambda message: not message.text.isdigit() or (
            int(message.text) < 0 or int(message.text) > 10),
        state=SubjectScoreForm.individual_achievements,
    )
    dp.register_message_handler(
        process_individual_archivments,
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

    # Объявление и инициализация объектов бота и диспетчера
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher(bot, storage=storage)

    # Регистрация хэндлеров
    register_all_handlers(dp)

    # Установка команд бота
    await set_commands(bot)

    # Запуск пуллинга
    executor.start_polling(dp, skip_updates=True)


if __name__ == "__main__":
    # Выполняется запуск бота, только если файл запускается напрямую,
    # а не импортируется
    nest_asyncio.apply()
    asyncio.run(main())
