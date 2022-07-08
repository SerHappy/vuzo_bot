from aiogram.dispatcher.filters.state import State, StatesGroup


class TestForm(StatesGroup):
    """
    Класс хранения состояний для рубрики "Тест на профориентацию"
    """
    answer_wait = State()
    result_wait = State()