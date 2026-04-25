from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from keyboards import get_main_keyboard
from logger import logger
from db_instance import db

router = Router()

gender_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Мужской", callback_data="gender_male")],
    [InlineKeyboardButton(text="Женский", callback_data="gender_female")]
])

@router.message(Command("start"))
async def command_start_handler(message: Message) -> None:
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.full_name
    logger.info(f"Пользователь @{username} (id: {user_id}) запустил бота")

    user = await db.get_user(user_id)
    if not user:
        user = {
            "user_id": user_id,
            "username": username,
            "first_name": message.from_user.first_name or "NoName",
            "goal": None,
            "streak": 0,
            "last_workout_date": None,
            "total_workouts": 0,
            "level": "easy",
            "workouts_on_level": 0,
            "gender": None,
            "gym_level": "pro1",
            "gym_workouts_count": 0,
            "gym_daily_count": 0,
            "gym_last_workout_date": None,
            "reminder_enabled": 1
        }
        await db.save_user(user)
        logger.info(f"Новый пользователь @{username} (id: {user_id}) зарегистрирован")

    if user["gender"] is None:
        await message.answer("Укажи свой пол:", reply_markup=gender_keyboard)
    else:
        await message.answer(
            "Ну, привет. \n"
            "Ты хочешь похудеть, набрать массу или подкачаться? \n"
            "Выбирай один из вариантов ниже, чтобы дать мне понять, что тебе нужно",
            reply_markup=get_main_keyboard(user_id, user.get("level"))
        )

@router.callback_query(lambda c: c.data.startswith("gender_"))
async def process_gender(callback: CallbackQuery):
    user_id = callback.from_user.id
    gender = callback.data.split("_")[1]
    await db.update_user(user_id, gender=gender)
    await callback.message.edit_text(f"Отлично! Теперь я буду обращаться к тебе в {('мужском', 'женском')[gender=='female']} роде.")
    user = await db.get_user(user_id)
    await callback.message.answer(
        "Ты хочешь похудеть, набрать массу или подкачаться?",
        reply_markup=get_main_keyboard(user_id, user.get("level") if user else None)
    )
    await callback.answer()