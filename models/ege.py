from aiogram.dispatcher.filters.state import State, StatesGroup


class SubjectScoreForm(StatesGroup):
    """
    Класс хранения состояний для рубрики "Калькулятор ЕГЭ"
    """
    amount_wait = State()
    subject_wait = State()
    score_wait = State()
    continue_wait = State()
    return_wait = State()
    individual_achievements_wait = State()
    search_wait = State()