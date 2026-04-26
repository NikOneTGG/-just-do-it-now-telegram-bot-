from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from config import ADMIN_IDS

# текст о технических работах
MAINTENANCE_TEXT = (
    "Бот временно на техническом обслуживании.\n"
    "Доступ ограничен.\n"
    "По вопросам:"
)

# Кнопка поддержки
SUPPORT_BUTTON = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Написать в поддержку", url="https://t.me/JDINOWBOTSUPPORT")]
])

class AuthMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        user_id = None
        if isinstance(event, Message):
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id

        if user_id and user_id not in ADMIN_IDS:
            if isinstance(event, Message):
                await event.answer(MAINTENANCE_TEXT, reply_markup=SUPPORT_BUTTON)
            elif isinstance(event, CallbackQuery):
                await event.answer()
                await event.message.answer(MAINTENANCE_TEXT, reply_markup=SUPPORT_BUTTON)
            return

        return await handler(event, data)