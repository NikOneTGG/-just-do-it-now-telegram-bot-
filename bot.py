import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.storage.memory import MemoryStorage
from config import TOKEN, PROXY_URL
from logger import logger
from handlers import start, goals, profile, workouts, navigation, misc, admin, advanced
from utils.scheduler import setup_scheduler
from middlewares.throttling import ThrottlingMiddleware
from db_instance import db

async def main():
    # proxy
    if PROXY_URL:
        session = AiohttpSession(proxy=PROXY_URL)
    else:
        session = AiohttpSession()
    bot = Bot(token=TOKEN, session=session)

    dp = Dispatcher(storage=MemoryStorage())
    dp.message.middleware(ThrottlingMiddleware(rate_limit=1.0))

    dp.include_router(start.router)
    dp.include_router(goals.router)
    dp.include_router(profile.router)
    dp.include_router(workouts.router)
    dp.include_router(navigation.router)
    dp.include_router(misc.router)
    dp.include_router(admin.router)
    dp.include_router(advanced.router)

    @dp.errors()
    async def global_error_handler(update, exception):
        logger.exception(f"Ошибка при обработке обновления {update}: {exception}")
        return True

    setup_scheduler(bot)

    logger.info("Бот запущен и готов к работе")

    try:
        await dp.start_polling(bot)
    finally:
        await session.close()
        logger.info("Сессия закрыта")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен пользователем")