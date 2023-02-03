from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from config.keyboards.markups import reply_keyboard, test_answers_keyboard
from .common import cancel_state
from FSM.test import TestForm
from config.tests import QUESTIONS, QUESTIONS_ANSWERS


async def start_fsm_for_test(message: types.Message, state=FSMContext) -> None:
    """Начало машины состояния для теста"""
    # Вызов функции сброса состояния
    await cancel_state(state)
    # Сброс всех ответов пользователя на тест
    async with state.proxy() as data:
        data["Nature"] = 0
        data["Technics"] = 0
        data["Human"] = 0
        data["Sign System"] = 0
        data["Artistic Image"] = 0
    # Формирование сообщения бота
    await message.answer(
        (
            "Привет, это тест на профориентацию!\n"
            "Тест состоит из 20 пар утверждений."
            "Внимательно прочитав оба утверждения, выбери то, "
            "которое больше соответствует твоему желанию."
            "Выбор нужно сделать в каждой паре утверждений!\n"
            "PS: Для ответов используй предложенные шаблоны сообщений"
        ),
        reply_markup=types.ReplyKeyboardRemove(),
    )
    await TestForm.answer_wait.set()
    # Вызов функции для формирования первого вопроса
    await process_answers(message, state)


async def process_answers(message: types.Message, state=FSMContext) -> None:
    """
    Обрабатывает ответ на тест и,
    либо запрашивает слудюущий ответ,
    либо сообщает о завершении теста
    """
    async with state.proxy() as data:
        # Увеличение значения ключа number в хранилище данных FSM
        data["number"] = data.setdefault("number", 0) + 1
    # Получение текущего состояния
    if data["number"] == 20:
        await TestForm.result_wait.set()
        # Формирование завершения теста
        keyboard = reply_keyboard("Узнать")
        answer = "Тест завершен!\nСкорее выбирай кнопку 'Узнать'"
        # Формирование сообщения бота
        await message.answer(answer, reply_markup=keyboard)
    else:
        # Формирование вопроса и пары ответов для теста
        keyboard = test_answers_keyboard(QUESTIONS[data["number"] - 1])
        answer = "Ответь на вопрос: «Мне нравится…»"
        # Формирование сообщения бота
        await message.answer(
            answer,
            reply_markup=keyboard,
        )


async def process_answer(message: types.Message, state=FSMContext) -> None:
    """
    Обработка ответов на вопрос
    и вызов функции для формирования следующего вопроса
    """
    async with state.proxy() as data:
        if message.text in QUESTIONS[data["number"] - 1]:
            # Обработка ответа на вопрос
            if message.text == QUESTIONS[data["number"] - 1][0]:
                data[QUESTIONS_ANSWERS[data["number"] - 1][0]] += 1
            if message.text == QUESTIONS[data["number"] - 1][1]:
                data[QUESTIONS_ANSWERS[data["number"] - 1][1]] += 1
            data["number"] += 1
            # Вызов функции для формирования следующего вопроса
            await process_answers(message, state)
        else:
            await message.answer("Нет такого варианта ответа! Выберите из предложенных!")


async def proccess_test_result(message: types.Message, state=FSMContext) -> None:
    """Выводит результаты теста"""
    data = await state.get_data()
    # Формирование теста ответа бота
    answer = "Ваш результат:\n\n"
    answer += (
        f"Человек — природа {int((data['Nature'] * 100)/8)}%\n"
        f"Человек — техника {int((data['Technics'] * 100)/8)}%\n"
        f"Человек — человек {int((data['Human'] * 100)/8)}%\n"
        f"Человек — знаковая система "
        f"{int((data['Sign System'] * 100)/8)}%\n"
        f"Человек — художественный образ "
        f"{int((data['Artistic Image'] * 100)/8)}%"
    )
    answer += (
        "\n\nЧеловек — природа.\n"
        "Сюда входят профессии, в которых человек имеет дело "
        "с различными явлениями неживой и живой природы, "
        "например биолог, географ, геолог, "
        "математик, физик, химик и другие профессии, "
        "относящиеся к разряду естественных наук."
    )
    answer += (
        "\n\nЧеловек — техника.\n"
        "В эту группу профессий включены различные виды трудовой "
        "деятельности, в которых человек  имеет дело с техникой, "
        "её использованием или конструированием, например профессия "
        "инженера, оператора, машиниста, "
        "механизатора, сварщика и т.п."
    )
    answer += (
        "\n\nЧеловек — человек.\n"
        "Сюда включены все виды профессий, предполагающих "
        "взаимодействие людей, например политика, религия, "
        "педагогика, психология, медицина, торговля, право."
    )
    answer += (
        "\n\nЧеловек — знаковая система.\n"
        "В эту группу включены профессии, касающиеся создания, "
        "изучения и использования различных знаковых систем, "
        "например лингвистика, языки математического "
        "программирования, способы графического представления "
        "результатов наблюдений и т.п."
    )
    answer += (
        "\n\nЧеловек — художественный образ.\n"
        "Эта группа профессий представляет собой различные "
        "виды художественно-творческого труда, например литература, "
        "музыка, театр, изобразительное искусство."
    )
    # Формирование сообщения бота
    await message.answer(answer, reply_markup=reply_keyboard())


def register_test_handlers(dp: Dispatcher):
    dp.register_message_handler(
        start_fsm_for_test,
        commands="test",
        state="*",
    )
    dp.register_message_handler(
        start_fsm_for_test,
        lambda message: message.text in ["Тест на профориентацию ℹ️"],
        state="*",
    )
    dp.register_message_handler(
        start_fsm_for_test,
        lambda message: message.text in ["Заново"],
        state=TestForm.result_wait,
    )
    dp.register_message_handler(
        process_answer,
        state=TestForm.answer_wait,
    )
    dp.register_message_handler(
        proccess_test_result,
        lambda message: message.text in "Узнать",
        state=TestForm.result_wait,
    )
