from aiogram.dispatcher.filters.state import State, StatesGroup


class RatingForm(StatesGroup):
    """
    Класс хранения состояний для рубрики "Рейтинги вызов"
    """

    rating_wait = State()

