from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from config import ADMIN_IDS

MAINTENANCE_TEXT = (
    "Бот временно на техническом обслуживании.\n"
    "Доступ ограничен.\n"
    "По вопросам:"
)

SUPPORT_BUTTON = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Написать поддержку", url="https://t.me/JDINOWBOTSUPPORT")]
])

class AuthMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        user_id = None
        if isinstance(event, Message):
            user_id = event.from_user.id
            # команда /admin должна обрабатываться всегда (даже если не админ)
            if event.text == "/admin":
                return await handler(event, data)
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id

        # отладка
        print(f"AuthMiddleware: user_id={user_id}, ADMIN_IDS={ADMIN_IDS}")

        if user_id and user_id not in ADMIN_IDS:
            # Блокировка запроса не от админа
            if isinstance(event, Message):
                await event.answer(MAINTENANCE_TEXT, reply_markup=SUPPORT_BUTTON)
            elif isinstance(event, CallbackQuery):
                await event.answer() 
                await event.message.answer(MAINTENANCE_TEXT, reply_markup=SUPPORT_BUTTON)
            return

        # вход для админов
        return await handler(event, data)