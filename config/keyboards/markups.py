from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from ..subjects import subjects

back = "Назад в меню 🔙"


def _create_markup(buttons):
    """Private function to create keyboard"""
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for button in buttons:
        markup.add(KeyboardButton(button))
    return markup


def _add_extra_buttons(markup: ReplyKeyboardMarkup, buttons: tuple[str, ...]):
    """Private funcion to add buttons to markup"""
    for button in buttons:
        markup.add(KeyboardButton(button))


def menu_keyboard(*args: str) -> ReplyKeyboardMarkup:
    """Шаблоны сообщений с главными рубриками"""
    print(args)
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


def test_answers_keyboard(*args: str) -> ReplyKeyboardMarkup:
    """Create keyboard for TEST case with given buttons"""
    return _create_markup(args)


def ratings_keyboard(*args: str) -> ReplyKeyboardMarkup:
    """Create keyboard for RATING case with given buttons"""
    return _create_markup(args)


def subject_keyboard(*args: str) -> ReplyKeyboardMarkup:
    """Create keyboard for EGE CALCULATING case with subjects and given buttons"""
    markup = _create_markup(subjects)

    if args:
        _add_extra_buttons(markup, args)

    return markup
