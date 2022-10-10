import json
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from config.keyboards.markups import reply_keyboard, subject_keyboard
from data.parsing.mirea.parsing import (
    get_exams,
    create_xlsx_directions,
    load_all_directions,
    get_ids,
)
from userscore import user_scores
from .common import cancel_state
from FSM.ege import SubjectScoreForm
from config.subjects import subjects
from decouple import config
import os

# from config.universities import universities
from handlers.common import empty


async def start_fsm_for_subject(message: types.Message, state=FSMContext) -> None:
    """Начинает машину состояния для Калькулятора ЕГЭ"""
    # Сброс всех данных о предметах пользователя
    user_scores.clear()
    # Вызов функции сброса состояния
    await cancel_state(state)
    # Установка состояния в "ожидание ввода кол-ва сданных предметов"
    await SubjectScoreForm.amount_wait.set()
    # Формирование сообщения бота
    await message.answer(
        "Введи кол-во предметов, которые ты сдавал/а:",
        reply_markup=types.ReplyKeyboardRemove(),
    )


async def process_amount_invalid(message: types.Message) -> None:
    """
    Сообщает об ошибке,
    если количество предметов введено неверно
    """
    # Формирование сообщения бота
    await message.answer(
        (
            f"Количество предметов дожно быть в диапозоне от 3 до "
            f"{len(subjects)}\nВведи корректные данные:"
        )
    )


async def process_amount(message: types.Message, state=FSMContext) -> None:
    """Обрабатывает количество предметов и запрашивает ввод предмета"""
    async with state.proxy() as data:
        if await state.get_state() == "SubjectScoreForm:amount_wait":
            # Запись в хранилище данных FSM по ключу amount
            # кол-во предметов, если текущее состояние
            # "ожидание ввода кол-ва предметов"
            data["amount"] = int(message.text)
    # Формирование шаблонов сообщений,
    # содержащих все предметы, ДВИ и пункт 'Назад в меню'
    keyboard = subject_keyboard()
    # Установка состояния в "ожидание ввода предмета"
    await SubjectScoreForm.subject_wait.set()
    # Формирование сообщения бота
    await message.answer("Выбери предмет, который ты сдавал:", reply_markup=keyboard)


async def process_subject_invalid(message: types.Message) -> None:
    """Сообщает об ошибке, если предмет введен неверно"""
    return await message.reply(("Неверный ввод предмета!\n" "Введи корректные данные:"))


async def process_subject(message: types.Message, state=FSMContext) -> None:
    """Обрабатывает введеный предмет и запрашивает ввод баллов"""
    async with state.proxy() as data:
        # Запись в хранилище данных FSM
        # по ключу subject название предмета
        data["subject"] = message.text
    # Установка состояния в "ожидание ввода предмета"
    await SubjectScoreForm.score_wait.set()
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
    """
    Обрабатывает введенные баллы за предмет и,
    либо выводит сообщение о продолжении,
    либо сообщает об ошибке и просит начать сначала
    """
    async with state.proxy() as data:
        # Запись в хранилище данных FSM
        # по ключу score количества баллов
        data["score"] = int(message.text)
    # Добавление в словарь user_scores пары
    # (Название предмета:кол-во баллов)
    user_scores[data["subject"]] = data["score"]
    if len(user_scores) < data["amount"]:
        # Установка состояния в "ожидание ввода предмета,
        # если предметов введено меньше, чем число,
        # хранящиеся по ключу amount в хранилище данных FSM"
        await SubjectScoreForm.subject_wait.set()
        # Вызов запрашивания ввода предмета
        await process_amount(message, state=state)
    else:
        # Формирование шаблонов сообщений
        # путем глубокого копирования reply_keyboard
        if "Математика (профиль)" in user_scores and "Русский язык" in user_scores:
            # Если пользователь ввел баллы за два обязательных предмета
            # (Математика и Русский языкы)
            # Добалвение еще одного шаблона
            keyboard = reply_keyboard("Продолжить")
            #
            text = "Вы можете перейти к подбору факультетов!"
            # Установка состояния "ожидание ввода кнопки Продолжить",
            await SubjectScoreForm.continue_wait.set()
        else:
            # Установка состояния в "Ожидание ввода Заново"
            await SubjectScoreForm.return_wait.set()
            text = (
                "Вы должны добавить баллы за обязательные предметы "
                "(Математика и Русский язык)"
            )
            keyboard = reply_keyboard()
        # Формирование сообщения бота
        await message.answer(text, reply_markup=keyboard)


async def process_individual_archivments_start(
    message: types.Message, state=FSMContext
) -> None:
    """
    Запрашивает у пользователя ввод количества дополнительных баллов
    """
    # получение всех данных из хранилища данных FSM
    data = await state.get_data()
    if (
        "Математика (профиль)" in user_scores
        and "Русский язык" in user_scores
        and len(user_scores) == data["amount"]
    ):
        # Установка состояния "ожидание ввода кол-ва баллов за ИД",
        # если введены баллы за обязательные предметы и кол-во
        # введенных предметов равно data["amount"]
        await SubjectScoreForm.individual_achievements_wait.set()
        # Формирование ответа
        await message.answer(
            "Введи кол-во доп. баллов (введи 0, если их нет): ",
            reply_markup=types.ReplyKeyboardRemove(),
        )
    else:
        # Вызов метода обработки неизвестного текста
        await empty(message)


async def process_individual_archivments_invalid(message: types.Message) -> None:
    """Сообщает об ошибке, если дополнительные баллы введены неверно"""
    # Формирование сообщения бота
    return await message.reply(
        (
            "Доп. баллы должны быть в диапазоне от 0 до 10!\n"
            "Введите корректные данные: "
        )
    )


async def process_individual_archivments(
    message: types.Message, state=FSMContext
) -> None:
    """
    Обработывает дополнительные баллы
    и выводит данные пользователя о сданных предметах и ИД
    """
    async with state.proxy() as data:
        # Запись в хранилище данных FSM
        # по ключу individual_achievements_value кол-ва баллов за ИД
        data["individual_achievements_value"] = int(message.text)
    individual_achievements_value = data["individual_achievements_value"]
    # Вызов функции сброса состояния
    answer = f"Добавлено {individual_achievements_value} баллов!"
    # Формирование первого сообщения бота
    await message.answer(answer)
    answer = (
        f"Текущие введенные значения:\n" f"Количество предметов: {len(user_scores)}\n"
    )
    total_score = 0
    for subject, score in user_scores.items():
        # Добавление в переменную answer информации о предмете
        answer += f"Предмет '{subject}', баллов - {score}\n"
        # Прибавл. к переменной общих баллов кол-ва баллов за предмет
        total_score += score
    if individual_achievements_value > 0:
        answer += f"\nКоличество доп. баллов - " f"{individual_achievements_value}"
        # Прибавление к переменной общих баллов кол-ва баллов за ИД
        total_score += individual_achievements_value
    answer += f"\nОбщая сумма баллов равна: " f"{total_score}"
    # Формирование шаблонов сообщений
    keyboard = reply_keyboard("Подбор факультетов")
    # Установка состояния в "ожидание ввода текста: Подбор факультетов"
    await SubjectScoreForm.search_wait.set()
    # Формирование сообщения бота
    await message.answer(answer, reply_markup=keyboard)


async def process_search_start(message: types.Message, state=FSMContext) -> None:
    """
    Отправка пользователю подходящих факультетов
    или сообщения об их отсутствии
    """
    data = await state.get_data()
    individual_achievements_value = data["individual_achievements_value"]
    await message.answer("Идет загрузка, пожалуйста, подождите...")
    find = create_xlsx_directions(individual_achievements_value)
    # Переменная флаг. True - найден хотя бы 1 факультет, иначе False
    if not find:
        # Не найдено ни одно подходящее направление
        text = "К сожалению, мне не удалось найти подходящие факультеты"
        # Формирование сообщения бота
        await message.answer(text, reply_markup=reply_keyboard())
    else:
        await message.answer_document(
            open(
                os.path.join(
                    config("PROJECT_DIR"),
                    f"data/parsing/mirea/Факультеты.xlsx",
                ),
                "rb",
            )
        )
        await message.answer(
            "Вот все, что я смог найти!", reply_markup=reply_keyboard()
        )


def register_ege_handlers(db: Dispatcher):
    db.register_message_handler(
        start_fsm_for_subject,
        lambda message: message.text in ["Калькулятор баллов ЕГЭ 🧮"],
        state="*",
    )
    db.register_message_handler(
        start_fsm_for_subject,
        commands="ege",
        state="*",
    )
    db.register_message_handler(
        start_fsm_for_subject,
        lambda message: message.text in ["Заново"],
        state=SubjectScoreForm.amount_wait,
    )
    db.register_message_handler(
        start_fsm_for_subject,
        lambda message: message.text in ["Заново"],
        state=SubjectScoreForm.subject_wait,
    )
    db.register_message_handler(
        start_fsm_for_subject,
        lambda message: message.text in ["Заново"],
        state=SubjectScoreForm.score_wait,
    )
    db.register_message_handler(
        start_fsm_for_subject,
        lambda message: message.text in ["Заново"],
        state=SubjectScoreForm.search_wait,
    )
    db.register_message_handler(
        start_fsm_for_subject,
        lambda message: message.text in ["Заново"],
        state=SubjectScoreForm.individual_achievements_wait,
    )
    db.register_message_handler(
        start_fsm_for_subject,
        lambda message: message.text in ["Заново"],
        state=SubjectScoreForm.return_wait,
    )
    db.register_message_handler(
        process_amount_invalid,
        lambda message: not message.text.isdigit()
        or (int(message.text) < 3 or int(message.text) > len(subjects)),
        state=SubjectScoreForm.amount_wait,
    )
    db.register_message_handler(
        process_amount,
        lambda message: int(message.text) in range(3, len(subjects) + 1),
        state=SubjectScoreForm.amount_wait,
    )
    db.register_message_handler(
        process_subject_invalid,
        lambda message: message.text not in subjects,
        state=SubjectScoreForm.subject_wait,
    )
    db.register_message_handler(
        process_subject,
        lambda message: message.text in subjects,
        state=SubjectScoreForm.subject_wait,
    )
    db.register_message_handler(
        process_score_invalid,
        lambda message: message.text != "Продолжить"
        and (
            not message.text.isdigit()
            or (int(message.text) < 0 or int(message.text) > 100)
        ),
        state=SubjectScoreForm.score_wait,
    )
    db.register_message_handler(
        process_score,
        lambda message: message.text.isdigit(),
        state=SubjectScoreForm.score_wait,
    )
    db.register_message_handler(
        process_individual_archivments_start,
        lambda message: message.text == "Продолжить",
        state=SubjectScoreForm.continue_wait,
    )
    db.register_message_handler(
        process_individual_archivments_invalid,
        lambda message: not message.text.isdigit()
        or (int(message.text) < 0 or int(message.text) > 10),
        state=SubjectScoreForm.individual_achievements_wait,
    )
    db.register_message_handler(
        process_individual_archivments,
        lambda message: message.text.isdigit(),
        state=SubjectScoreForm.individual_achievements_wait,
    )
    db.register_message_handler(
        process_search_start,
        lambda message: message.text in ["Подбор факультетов"],
        state=SubjectScoreForm.search_wait,
    )
