import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.storage.memory import MemoryStorage
from config import TOKEN, PROXY_URL, ADMIN_IDS
from logger import logger
from handlers import goals, workouts, profile, misc, admin, advanced
from utils.scheduler import setup_scheduler
from middlewares.throttling import ThrottlingMiddleware
from db_instance import db

async def main():

    session = AiohttpSession()
    bot = Bot(token=TOKEN, session=session)

    dp = Dispatcher(storage=MemoryStorage())
    dp.message.middleware(ThrottlingMiddleware(rate_limit=1.0))

    # роутеры (только инлайн-версии)
    dp.include_router(goals.router)
    dp.include_router(workouts.router)
    dp.include_router(profile.router)
    dp.include_router(misc.router)
    dp.include_router(admin.router)
    dp.include_router(advanced.router)

    # глобальный обработчик ошибок
    @dp.errors()
    async def global_error_handler(update, exception):
        logger.exception(f"Ошибка: {update}\n{exception}")
        return True

    # планировщик
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