from aiogram.dispatcher.filters.state import State, StatesGroup


class TestForm(StatesGroup):
    """
    Класс хранения состояний для рубрики "Тест на профориентацию"
    """
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
    result_wait = State()