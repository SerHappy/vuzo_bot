from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from config.keyboards.markups import reply_keyboard, test_answers_keyboard
from .common import cancel_state
from models.test import TestForm
from config.tests import questions


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
    current_state = await state.get_state()
    if current_state is None:
        # Установка состояния в первое состояние класса TestForm
        await TestForm.first()
    else:
        # Установка состояния в следующее состояние класса TestForm
        await TestForm.next()
    # Получение текущего состояния
    current_state = await state.get_state()
    if current_state == "TestForm:result_wait":
        # Формирование завершения теста
        keyboard = reply_keyboard("Узнать")
        answer = "Тест завершен!\nСкорее выбирай кнопку 'Узнать'"
        # Формирование сообщения бота
        await message.answer(answer, reply_markup=keyboard)
    else:
        # Формирование вопроса и пары ответов для теста
        keyboard = test_answers_keyboard(questions[data["number"] - 1])
        if current_state == "TestForm:answer1_wait":
            # Текст ответа, если состояние "Ожидание первого ответа"
            answer = "Ответь на вопрос: «Мне нравится…»"
        else:
            answer = "Принято!\nОтветь на вопрос: «Мне нравится…»"
        # Формирование сообщения бота
        await message.answer(
            answer,
            reply_markup=keyboard,
        )


async def process_answer_1(message: types.Message, state=FSMContext) -> None:
    """
    Обработка ответа на вопрос 1
    и вызов функции для формирования следующего вопроса
    """
    async with state.proxy() as data:
        # Обработка ответа на вопрос
        if message.text == questions[0][0]:
            data["Nature"] += 1
        if message.text == questions[0][1]:
            data["Technics"] += 1
    # Вызов функции для формирования следующего вопроса
    await process_answers(message, state)


async def process_answer_2(message: types.Message, state=FSMContext) -> None:
    """
    Обработка ответа на вопрос 2
    и вызов функции для формирования следующего вопроса
    """
    async with state.proxy() as data:
        # Обработка ответа на вопрос
        if message.text == questions[1][0]:
            data["Human"] += 1
        if message.text == questions[1][1]:
            data["Sign System"] += 1
    # Вызов функции для формирования следующего вопроса
    await process_answers(message, state)


async def process_answer_3(message: types.Message, state=FSMContext) -> None:
    """
    Обработка ответа на вопрос 3
    и вызов функции для формирования следующего вопроса
    """
    async with state.proxy() as data:
        # Обработка ответа на вопрос
        if message.text == questions[2][0]:
            data["Artistic Image"] += 1
        if message.text == questions[2][1]:
            data["Nature"] += 1
    # Вызов функции для формирования следующего вопроса
    await process_answers(message, state)


async def process_answer_4(message: types.Message, state=FSMContext) -> None:
    """
    Обработка ответа на вопрос 4
    и вызов функции для формирования следующего вопроса
    """
    async with state.proxy() as data:
        # Обработка ответа на вопрос
        if message.text == questions[3][0]:
            data["Technics"] += 1
        if message.text == questions[3][1]:
            data["Human"] += 1
    # Вызов функции для формирования следующего вопроса
    await process_answers(message, state)


async def process_answer_5(message: types.Message, state=FSMContext) -> None:
    """
    Обработка ответа на вопрос 5
    и вызов функции для формирования следующего вопроса
    """
    async with state.proxy() as data:
        # Обработка ответа на вопрос
        if message.text == questions[4][0]:
            data["Sign System"] += 1
        if message.text == questions[4][1]:
            data["Artistic Image"] += 1
    # Вызов функции для формирования следующего вопроса
    await process_answers(message, state)


async def process_answer_6(message: types.Message, state=FSMContext) -> None:
    """
    Обработка ответа на вопрос 6
    и вызов функции для формирования следующего вопроса
    """
    async with state.proxy() as data:
        # Обработка ответа на вопрос
        if message.text == questions[5][0]:
            data["Nature"] += 1
        if message.text == questions[5][1]:
            data["Human"] += 1
    # Вызов функции для формирования следующего вопроса
    await process_answers(message, state)


async def process_answer_7(message: types.Message, state=FSMContext) -> None:
    """
    Обработка ответа на вопрос 7
    и вызов функции для формирования следующего вопроса
    """
    async with state.proxy() as data:
        # Обработка ответа на вопрос
        if message.text == questions[6][0]:
            data["Artistic Image"] += 1
        if message.text == questions[6][1]:
            data["Technics"] += 1
    # Вызов функции для формирования следующего вопроса
    await process_answers(message, state)


async def process_answer_8(message: types.Message, state=FSMContext) -> None:
    """
    Обработка ответа на вопрос 8
    и вызов функции для формирования следующего вопроса
    """
    async with state.proxy() as data:
        # Обработка ответа на вопрос
        if message.text == questions[7][0]:
            data["Human"] += 1
        if message.text == questions[7][1]:
            data["Artistic Image"] += 1
    # Вызов функции для формирования следующего вопроса
    await process_answers(message, state)


async def process_answer_9(message: types.Message, state=FSMContext) -> None:
    """
    Обработка ответа на вопрос 9
    и вызов функции для формирования следующего вопроса
    """
    async with state.proxy() as data:
        # Обработка ответа на вопрос
        if message.text == questions[8][0]:
            data["Technics"] += 1
        if message.text == questions[8][1]:
            data["Sign System"] += 1
    # Вызов функции для формирования следующего вопроса
    await process_answers(message, state)


async def process_answer_10(message: types.Message, state=FSMContext) -> None:
    """
    Обработка ответа на вопрос 10
    и вызов функции для формирования следующего вопроса
    """
    async with state.proxy() as data:
        # Обработка ответа на вопрос
        if message.text == questions[9][0]:
            data["Nature"] += 1
        if message.text == questions[9][1]:
            data["Sign System"] += 1
    # Вызов функции для формирования следующего вопроса
    await process_answers(message, state)


async def process_answer_11(message: types.Message, state=FSMContext) -> None:
    """
    Обработка ответа на вопрос 11
    и вызов функции для формирования следующего вопроса
    """
    async with state.proxy() as data:
        # Обработка ответа на вопрос
        if message.text == questions[10][0]:
            data["Nature"] += 1
        if message.text == questions[10][1]:
            data["Technics"] += 1
    # Вызов функции для формирования следующего вопроса
    await process_answers(message, state)


async def process_answer_12(message: types.Message, state=FSMContext) -> None:
    """
    Обработка ответа на вопрос 12
    и вызов функции для формирования следующего вопроса
    """
    async with state.proxy() as data:
        # Обработка ответа на вопрос
        if message.text == questions[11][0]:
            data["Human"] += 1
        if message.text == questions[11][1]:
            data["Sign System"] += 1
    # Вызов функции для формирования следующего вопроса
    await process_answers(message, state)


async def process_answer_13(message: types.Message, state=FSMContext) -> None:
    """
    Обработка ответа на вопрос 13
    и вызов функции для формирования следующего вопроса
    """
    async with state.proxy() as data:
        # Обработка ответа на вопрос
        if message.text == questions[12][0]:
            data["Artistic Image"] += 1
        if message.text == questions[12][1]:
            data["Nature"] += 1
    # Вызов функции для формирования следующего вопроса
    await process_answers(message, state)


async def process_answer_14(message: types.Message, state=FSMContext) -> None:
    """
    Обработка ответа на вопрос 14
    и вызов функции для формирования следующего вопроса
    """
    async with state.proxy() as data:
        # Обработка ответа на вопрос
        if message.text == questions[13][0]:
            data["Technics"] += 1
        if message.text == questions[13][1]:
            data["Human"] += 1
    # Вызов функции для формирования следующего вопроса
    await process_answers(message, state)


async def process_answer_15(message: types.Message, state=FSMContext) -> None:
    """
    Обработка ответа на вопрос 15
    и вызов функции для формирования следующего вопроса
    """
    async with state.proxy() as data:
        # Обработка ответа на вопрос
        if message.text == questions[14][0]:
            data["Sign System"] += 1
        if message.text == questions[14][1]:
            data["Artistic Image"] += 1
    # Вызов функции для формирования следующего вопроса
    await process_answers(message, state)


async def process_answer_16(message: types.Message, state=FSMContext) -> None:
    """
    Обработка ответа на вопрос 16
    и вызов функции для формирования следующего вопроса
    """
    async with state.proxy() as data:
        # Обработка ответа на вопрос
        if message.text == questions[15][0]:
            data["Nature"] += 1
        if message.text == questions[15][1]:
            data["Human"] += 1
    # Вызов функции для формирования следующего вопроса
    await process_answers(message, state)


async def process_answer_17(message: types.Message, state=FSMContext) -> None:
    """
    Обработка ответа на вопрос 17
    и вызов функции для формирования следующего вопроса
    """
    async with state.proxy() as data:
        # Обработка ответа на вопрос
        if message.text == questions[16][0]:
            data["Artistic Image"] += 1
        if message.text == questions[16][1]:
            data["Technics"] += 1
    # Вызов функции для формирования следующего вопроса
    await process_answers(message, state)


async def process_answer_18(message: types.Message, state=FSMContext) -> None:
    """
    Обработка ответа на вопрос 18
    и вызов функции для формирования следующего вопроса
    """
    async with state.proxy() as data:
        # Обработка ответа на вопрос
        if message.text == questions[17][0]:
            data["Human"] += 1
        if message.text == questions[17][1]:
            data["Artistic Image"] += 1
    # Вызов функции для формирования следующего вопроса
    await process_answers(message, state)


async def process_answer_19(message: types.Message, state=FSMContext) -> None:
    """
    Обработка ответа на вопрос 19
    и вызов функции для формирования следующего вопроса
    """
    async with state.proxy() as data:
        # Обработка ответа на вопрос
        if message.text == questions[18][0]:
            data["Technics"] += 1
        if message.text == questions[18][1]:
            data["Sign System"] += 1
    # Вызов функции для формирования следующего вопроса
    await process_answers(message, state)


async def process_answer_20(message: types.Message, state=FSMContext) -> None:
    """
    Обработка ответа на вопрос 20
    и вызов функции для вывода сообщения о завершении теста
    """
    async with state.proxy() as data:
        # Обработка ответа на вопрос
        if message.text == questions[19][0]:
            data["Nature"] += 1
        if message.text == questions[19][1]:
            data["Sign System"] += 1
    # Вызов функции для вывода сообщения о завершении теста
    await process_answers(message, state)


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
        process_answer_1,
        lambda message: message.text in questions[0],
        state=TestForm.answer1_wait,
    )
    dp.register_message_handler(
        process_answer_2,
        lambda message: message.text in questions[1],
        state=TestForm.answer2_wait,
    )
    dp.register_message_handler(
        process_answer_3,
        lambda message: message.text in questions[2],
        state=TestForm.answer3_wait,
    )
    dp.register_message_handler(
        process_answer_4,
        lambda message: message.text in questions[3],
        state=TestForm.answer4_wait,
    )
    dp.register_message_handler(
        process_answer_5,
        lambda message: message.text in questions[4],
        state=TestForm.answer5_wait,
    )
    dp.register_message_handler(
        process_answer_6,
        lambda message: message.text in questions[5],
        state=TestForm.answer6_wait,
    )
    dp.register_message_handler(
        process_answer_7,
        lambda message: message.text in questions[6],
        state=TestForm.answer7_wait,
    )
    dp.register_message_handler(
        process_answer_8,
        lambda message: message.text in questions[7],
        state=TestForm.answer8_wait,
    )
    dp.register_message_handler(
        process_answer_9,
        lambda message: message.text in questions[8],
        state=TestForm.answer9_wait,
    )
    dp.register_message_handler(
        process_answer_10,
        lambda message: message.text in questions[9],
        state=TestForm.answer10_wait,
    )
    dp.register_message_handler(
        process_answer_11,
        lambda message: message.text in questions[10],
        state=TestForm.answer11_wait,
    )
    dp.register_message_handler(
        process_answer_12,
        lambda message: message.text in questions[11],
        state=TestForm.answer12_wait,
    )
    dp.register_message_handler(
        process_answer_13,
        lambda message: message.text in questions[12],
        state=TestForm.answer13_wait,
    )
    dp.register_message_handler(
        process_answer_14,
        lambda message: message.text in questions[13],
        state=TestForm.answer14_wait,
    )
    dp.register_message_handler(
        process_answer_15,
        lambda message: message.text in questions[14],
        state=TestForm.answer15_wait,
    )
    dp.register_message_handler(
        process_answer_16,
        lambda message: message.text in questions[15],
        state=TestForm.answer16_wait,
    )
    dp.register_message_handler(
        process_answer_17,
        lambda message: message.text in questions[16],
        state=TestForm.answer17_wait,
    )
    dp.register_message_handler(
        process_answer_18,
        lambda message: message.text in questions[17],
        state=TestForm.answer18_wait,
    )
    dp.register_message_handler(
        process_answer_19,
        lambda message: message.text in questions[18],
        state=TestForm.answer19_wait,
    )
    dp.register_message_handler(
        process_answer_20,
        lambda message: message.text in questions[19],
        state=TestForm.answer20_wait,
    )
    dp.register_message_handler(
        proccess_test_result,
        lambda message: message.text in "Узнать",
        state=TestForm.result_wait,
    )
