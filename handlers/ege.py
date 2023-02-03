from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from config.keyboards.markups import reply_keyboard, subject_keyboard
from data.parsing.mirea.parsing import create_xlsx_directions
from .common import cancel_state
from FSM.ege import SubjectScoreForm
from config.subjects import subjects
from models.db import Session
from decouple import config
from db_utils import (
    add_user,
    get_association_user_subject_indv_record,
    get_association_user_subject_subject_id_by_user_id_desc,
    set_User_ege_subjects_number,
    get_User_ege_subjects_number,
    set_association_user_subject_subject_id_by_user_id,
    set_association_user_subject_score_by_desc_user_id,
    get_association_user_subject_records_count_by_user_id,
    set_association_user_subject_indv_score_for_user,
    get_association_user_subject_all_records_by_id,
    get_subject_name_by_id,
    set_User_ege_total_score,
    get_User_ege_total_score,
    delete_association_user_subject_records_by_user_id,
)
import os

# from config.universities import universities
from handlers.common import empty


async def start_fsm_for_subject(message: types.Message, state=FSMContext) -> None:
    """Начинает машину состояния для Калькулятора ЕГЭ"""
    user_id = message.from_user.id
    user_username = message.from_user.username
    add_user(user_id, user_username)
    # Сброс всех данных о предметах пользователя
    delete_association_user_subject_records_by_user_id(user_id)
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
        (f"Количество предметов дожно быть в диапозоне от 3 до " f"{len(subjects)}\nВведи корректные данные:")
    )


async def process_amount(message: types.Message, state=FSMContext) -> None:
    """Обрабатывает количество предметов и запрашивает ввод предмета"""
    async with state.proxy() as data:
        if await state.get_state() == "SubjectScoreForm:amount_wait":
            # Запись в хранилище данных FSM по ключу amount
            # кол-во предметов, если текущее состояние
            # "ожидание ввода кол-ва предметов"
            data["amount"] = int(message.text)
    if get_User_ege_subjects_number(message.from_user.id) == 0:
        user_id = message.from_user.id
        set_User_ege_subjects_number(user_id, int(message.text))
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

    set_association_user_subject_subject_id_by_user_id(message.from_user.id, message.text)
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
    return await message.reply("Баллы должны быть в диапазоне от 0 до 100!\nВведи корректные данные:")


async def process_score(message: types.Message, state=FSMContext) -> None:
    """
    Обрабатывает введенные баллы за предмет и,
    либо выводит сообщение о продолжении,
    либо сообщает об ошибке и просит начать сначала
    """
    set_association_user_subject_score_by_desc_user_id(
        message.from_user.id,
        get_association_user_subject_subject_id_by_user_id_desc(message.from_user.id),
        int(message.text),
    )
    # Добавление в словарь user_scores пары
    # (Название предмета:кол-во баллов)
    if get_association_user_subject_records_count_by_user_id(message.from_user.id) < get_User_ege_subjects_number(
        message.from_user.id
    ):
        # Установка состояния в "ожидание ввода предмета,
        # если предметов введено меньше, чем число,
        # хранящиеся по ключу amount в хранилище данных FSM"
        await SubjectScoreForm.subject_wait.set()
        # Вызов запрашивания ввода предмета
        await process_amount(message, state=state)
    else:
        # Формирование шаблонов сообщений
        # путем глубокого копирования reply_keyboard
        # if "Математика (профиль)" in user_scores and "Русский язык" in user_scores:
        if get_association_user_subject_records_count_by_user_id(message.from_user.id) == 3:
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
            text = "Вы должны добавить баллы за обязательные предметы " "(Математика и Русский язык)"
            keyboard = reply_keyboard()
        # Формирование сообщения бота
        await message.answer(text, reply_markup=keyboard)


async def process_individual_archivments_start(message: types.Message, state=FSMContext) -> None:
    """
    Запрашивает у пользователя ввод количества дополнительных баллов
    """
    # получение всех данных из хранилища данных FSM
    if get_association_user_subject_records_count_by_user_id(message.from_user.id) == 3:
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
    return await message.reply(("Доп. баллы должны быть в диапазоне от 0 до 10!\n" "Введите корректные данные: "))


async def process_individual_archivments(message: types.Message, state=FSMContext) -> None:
    """
    Обработывает дополнительные баллы
    и выводит данные пользователя о сданных предметах и ИД
    """
    if int(message.text) != 0:
        set_association_user_subject_indv_score_for_user(message.from_user.id, int(message.text))
        answer = f"Добавлено {message.text} баллов!"
        # Формирование первого сообщения бота
        await message.answer(answer)
    answer = (
        f"Текущие введенные значения:\n" f"Количество предметов: {get_User_ege_subjects_number(message.from_user.id)}\n"
    )
    total_score = 0
    session = Session()
    for ege_record in get_association_user_subject_all_records_by_id(message.from_user.id):
        # Добавление в переменную answer информации о предмете
        ege_record_subject_name = get_subject_name_by_id(session, ege_record.subject_id)
        answer += f"Предмет '{ege_record_subject_name}', баллов - {ege_record.score}\n"
        # Прибавл. к переменной общих баллов кол-ва баллов за предмет
        total_score += ege_record.score
        print(total_score, state)
    indv_record = get_association_user_subject_indv_record(message.from_user.id)
    if indv_record != None:
        answer += f"Кол-во доп баллов: {indv_record.score}\n"
        total_score += indv_record.score
    set_User_ege_total_score(message.from_user.id, total_score)
    # if individual_achievements_value > 0:
    #     answer += f"\nКоличество доп. баллов - " f"{individual_achievements_value}"
    #     # Прибавление к переменной общих баллов кол-ва баллов за ИД
    #     total_score += individual_achievements_value
    answer += f"\nОбщая сумма баллов равна: " f"{get_User_ege_total_score(message.from_user.id)}"
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
    await message.answer("Идет загрузка, пожалуйста, подождите...")
    find = create_xlsx_directions(message.from_user.id)
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
        await message.answer("Вот все, что я смог найти!", reply_markup=reply_keyboard())


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
        lambda message: not message.text.isdigit() or (int(message.text) < 3 or int(message.text) > len(subjects)),
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
        and (not message.text.isdigit() or (int(message.text) < 0 or int(message.text) > 100)),
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
        lambda message: not message.text.isdigit() or (int(message.text) < 0 or int(message.text) > 10),
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
