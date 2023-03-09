import asyncio
import os
import nest_asyncio
from create_database import create_database
from aiogram import Bot, types, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from handlers.common import register_common_handlers, register_empty_handler
from handlers.ege import register_ege_handlers
from handlers.ratings import register_ratings_handlers
from handlers.test import register_test_handlers
from decouple import config


async def set_commands(bot: Bot) -> None:
    """Регистрация команд, отображаемых в интерфейсе Telegram"""
    commands = [
        types.BotCommand(
            command="/start", description="Привественное сообщение"
        ),
        types.BotCommand(command="/menu", description="Главное меню"),
        types.BotCommand(command="/ege", description="Калькулятор баллов ЕГЭ"),
        types.BotCommand(command="/rating", description="Рейтинги вузов"),
        types.BotCommand(
            command="/test",
            description="Тест на определение типа будущей профессии",
        ),
    ]
    await bot.set_my_commands(commands)


def register_all_handlers(dp: Dispatcher):
    """Регестрирует хэндлеры для каждой функции"""
    register_common_handlers(dp)
    register_ege_handlers(dp)
    register_ratings_handlers(dp)
    register_test_handlers(dp)
    register_empty_handler(dp)


async def main():
    """Главный метод программы. Запускает бота"""

    # Объявление и инициализация объектов бота и диспетчера
    bot = Bot(token=str(config("BOT_TOKEN", cast=str)))
    dispatcher = Dispatcher(bot, storage=MemoryStorage())

    # Регистрация хэндлеров
    register_all_handlers(dispatcher)

    # Установка команд бота
    await set_commands(bot)

    # Создание базы данных
    db_is_created = os.path.exists("db.sqlite3")
    if not db_is_created:
        create_database()
    else:
        os.remove(f"{config('PROJECT_DIR')}/db.sqlite3")
        create_database()

    # Запуск пуллинга
    executor.start_polling(dispatcher, skip_updates=True)


if __name__ == "__main__":
    # Выполняется запуск бота, только если файл запускается напрямую,
    # а не импортируется
    nest_asyncio.apply()
    asyncio.run(main())
