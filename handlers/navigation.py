from aiogram import Router
from aiogram.types import Message
from keyboards import get_main_keyboard, get_workout_keyboard
from db_instance import db

router = Router()

@router.message(lambda message: message.text == "В главное меню")
async def main_menu_handler(message: Message) -> None:
    user_id = message.from_user.id
    user = await db.get_user(user_id)
    await message.answer(
        "Возвращаемся в главное меню. Выбирай цель:",
        reply_markup=get_main_keyboard(user_id, user.get("level") if user else None)
    )

@router.message(lambda message: message.text == "◀️ Назад")
async def back_from_profile_handler(message: Message) -> None:
    user_id = message.from_user.id
    user = await db.get_user(user_id)
    if user and user.get("goal"):
        await message.answer(
            "Возвращаемся к тренировке",
            reply_markup=get_workout_keyboard(user_id)
        )
    else:
        await message.answer(
            "Главное меню",
            reply_markup=get_main_keyboard(user_id, user.get("level") if user else None)
        )