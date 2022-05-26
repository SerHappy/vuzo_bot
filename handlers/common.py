from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from config.keyboards.markups import menu_keyboard


async def cancel_state(state=FSMContext):
    """Сбрасывает состояние и хранящиеся данные"""
    current_state = await state.get_state()
    if current_state is not None:
        await state.finish()


async def send_welcome_message(message: types.Message, state=FSMContext) -> None:
    """Отправляет приветственное сообщение"""
    # Вызов функции сброса состояния
    await cancel_state(state)
    # Формирование сообщения бота
    await message.answer(
        (
            f"Привет, {message.from_user.first_name}!\nЯ буду твоим "
            "путеводителем в мир вузов.\nВиртуальный помощник ищет "
            "образовательные программы высших профессиональный учебных "
            "заведений и помогает тебе определиться с местом, где ты проведёшь "
            "ближайшие 4 года. Здесь ты найдёшь всю интересующую тебя "
            "информацию: от наличия общежитий до проходных баллов.\n"
            "Посмотри все мои команды, набрав /menu, "
            "или воспользуйся шаблонами ниже, и скорее бери курс на вуз!"
        ),
        reply_markup=menu_keyboard("dfdfdfd"),
    )


async def main_menu(message: types.Message, state=FSMContext) -> None:
    """Прекращае любое состояние и показывает главное меню"""
    # Вызов функции сброса состояния
    await cancel_state(state)
    # Формирование сообщения бота
    await message.answer(
        (
            "Команды бота:\n"
            "/start - привественное сообщение\n"
            "/menu - главное меню\n"
            "/ege - Калькулятор баллов ЕГЭ\n"
            "/rating - Рейтинг вузов\n"
            "/test - Тест на определение типа будущей профессии\n"
            "Так же можешь воспользоваться кнопками с шаблонами сообщений :)\n"
            "(PS: Все команды прекращают текущее действие и начинают новое, "
            "так что буть осторожен при их использовании!"
        ),
        reply_markup=menu_keyboard(),
    )


async def empty(message: types.Message) -> None:
    """Обрабатывает неотловленные команды/сообщения"""
    # Формирование сообщения бота
    await message.answer(
        "Неизвестый текст.\nВведите /menu для просмотра всех команд бота"
    )


def register_common_handlers(dp: Dispatcher):
    dp.register_message_handler(
        main_menu,
        commands=["menu"],
        state="*",
    )
    dp.register_message_handler(
        main_menu,
        lambda message: message.text.lower()
        in ["главное меню", "меню", "назад в меню 🔙", "назад"],
        state="*",
    )
    dp.register_message_handler(
        send_welcome_message, commands=["start", "help"], state="*"
    )


def register_empty_handler(dp: Dispatcher):
    dp.register_message_handler(empty, state="*")
