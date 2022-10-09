import asyncio
import nest_asyncio
from aiogram import Bot, types, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from handlers import common, ege, ratings, test
from decouple import config


async def on_startup(_):
    print("Бот запущен")


async def on_shutdown(_):
    print("Бот остановлен")


async def set_commands(bot: Bot) -> None:
    """Регистрация команд, отображаемых в интерфейсе Telegram"""
    commands = [
        types.BotCommand(command="/start", description="Привественное сообщение"),
        types.BotCommand(command="/menu", description="Главное меню"),
        types.BotCommand(command="/ege", description="Калькулятор баллов ЕГЭ"),
        types.BotCommand(command="/rating", description="Рейтинги вузов"),
        types.BotCommand(
            command="/test", description="Тест на определение типа будущей профессии"
        ),
    ]
    await bot.set_my_commands(commands)


def register_all_handlers(dp: Dispatcher):
    """Регестрирует хэндлеры для каждой функции"""
    common.register_common_handlers(dp)
    ege.register_ege_handlers(dp)
    ratings.register_ratings_handlers(dp)
    test.register_test_handlers(dp)
    common.register_empty_handler(dp)


async def main():
    """Главный метод программы. Запускает бота"""
    storage = MemoryStorage()

    # Объявление и инициализация объектов бота и диспетчера
    bot = Bot(token=config("BOT_TOKEN", cast=str))
    dispatcher = Dispatcher(bot, storage=storage)

    # Регистрация хэндлеров
    register_all_handlers(dispatcher)

    # Установка команд бота
    await set_commands(bot)

    # Запуск пуллинга
    executor.start_polling(
        dispatcher, skip_updates=True, on_startup=on_startup, on_shutdown=on_shutdown
    )


if __name__ == "__main__":
    # Выполняется запуск бота, только если файл запускается напрямую,
    # а не импортируется
    nest_asyncio.apply()
    asyncio.run(main())
