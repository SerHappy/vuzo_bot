from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from ..subjects import subjects
from ..ratings import ratings_names

back = "Назад в меню 🔙"


def _create_markup(args):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for arg in args:
        markup.add(KeyboardButton(arg))

    return markup


def _add_extra_buttons(markup: ReplyKeyboardMarkup, buttons: tuple[str]):
    for button in buttons:
        markup.add(KeyboardButton(button))


def menu_keyboard(*args: str) -> ReplyKeyboardMarkup:
    """Шаблоны сообщений с главными рубриками"""
    markup = (
        ReplyKeyboardMarkup(resize_keyboard=True)
        .add(KeyboardButton("Калькулятор баллов ЕГЭ 🧮"))
        .add(KeyboardButton("Рейтинги вузов 🔝"))
        .add(KeyboardButton("Тест на профориентацию ℹ️"))
    )
    if args:
        _add_extra_buttons(markup, args)

    return markup


def reply_keyboard(*args: str) -> ReplyKeyboardMarkup:
    """Шаблоны сообщений для возврата назад или в меню"""
    markup = (
        ReplyKeyboardMarkup(
            resize_keyboard=True,
        )
        .add(KeyboardButton("Заново"))
        .add(KeyboardButton("Главное меню"))
    )
    if args:
        _add_extra_buttons(markup, args)

    return markup


def test_answers_keyboard(answers: str):
    return _create_markup(answers)


def ratings_keyboard(args: str):
    markup = _create_markup(subjects)

    if args:
        _add_extra_buttons(markup, args)

    return markup


def subject_keyboard(args: str):
    markup = _create_markup(subjects)

    if args:
        _add_extra_buttons(markup, args)

    return markup
