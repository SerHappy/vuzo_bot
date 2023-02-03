from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from config.keyboards.markups import reply_keyboard, ratings_keyboard
from .common import cancel_state
from config.ratings import (
    QS_WORLD_UNIVERSITY_RANKINGS_2022,
    TIMES_HIGHER_EDUCATION_WORLD_UNIVERSITY_RANKINGS_2022,
)
from FSM.ratings import RatingForm


async def start_fsm_for_rating(message: types.Message, state=FSMContext) -> None:
    """Начанает машину состояния для рейтингов вузов"""
    # Вызов функции сброса состояния
    await cancel_state(state)
    # Установка состояния в "Ожидание ввода названия рейтинга"
    await RatingForm.rating_wait.set()
    # Формирование шаблонов сообщений
    buttons = (
        "QS World University Rankings – 2022",
        "Times Higher Education World University Rankings – 2022",
    )
    keyboard = ratings_keyboard(*buttons)
    # Формирование сообщения бота
    await message.answer(
        "Выбери, какой рейтинг хочешь посмотреть",
        reply_markup=keyboard,
    )


async def process_rating_invalid(message: types.Message) -> None:
    """Сообщает об ошибке, если название рейтинга введено неверно"""
    return await message.reply("Такого рейтинга у меня нет :(\nВведи корректные данные: ")


async def process_rating(message: types.Message) -> None:
    """Обработывает название рейтинга вузов и выводит его"""
    # Проверка, какой рейтинг надо показать
    rating_to_show = (
        QS_WORLD_UNIVERSITY_RANKINGS_2022
        if message.text == "QS World University Rankings – 2022"
        else TIMES_HIGHER_EDUCATION_WORLD_UNIVERSITY_RANKINGS_2022
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
        answer += f"\n\n{university_name} -" f" {university_global} место в мире," f" {university_local} место в России"
    # Формирование сообщения бота
    await message.answer(
        answer,
        reply_markup=reply_keyboard(),
    )


def register_ratings_handlers(dp: Dispatcher):
    dp.register_message_handler(
        start_fsm_for_rating,
        commands="rating",
        state="*",
    )
    dp.register_message_handler(
        start_fsm_for_rating,
        lambda message: message.text in ["Рейтинги вузов 🔝"],
        state="*",
    )
    dp.register_message_handler(
        start_fsm_for_rating,
        lambda message: message.text in ["Заново"],
        state=RatingForm.rating_wait,
    )
    dp.register_message_handler(
        process_rating_invalid,
        lambda message: message.text
        not in [
            "QS World University Rankings – 2022",
            "Times Higher Education World University Rankings – 2022",
        ],
        state=RatingForm.rating_wait,
    )
    dp.register_message_handler(
        process_rating,
        lambda message: message.text
        in [
            "QS World University Rankings – 2022",
            "Times Higher Education World University Rankings – 2022",
        ],
        state=RatingForm.rating_wait,
    )
