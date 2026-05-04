from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from inlinekey import main_menu, gender_keyboard
from db_instance import db

router = Router()

# команда /start
@router.message(Command("start"))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.full_name
    replydelete = await message.answer("ㅤ", reply_markup=types.ReplyKeyboardRemove())
    await replydelete.delete()

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

    if user["gender"] is None:
        await message.answer("Укажи свой пол:", reply_markup=gender_keyboard())
    else:
        temp_msg = await message.answer("ㅤ")
        await temp_msg.delete()
        await message.answer(
            "Ну, привет.\nТы хочешь похудеть, набрать массу или подкачаться?",
            reply_markup=main_menu()
        )

# выбор цели
@router.callback_query(F.data.startswith("gender_"))
async def set_gender(callback: CallbackQuery):
    user_id = callback.from_user.id
    gender = callback.data.split("_")[1]
    await db.update_user(user_id, gender=gender)
    await callback.message.delete()
    await callback.message.answer(
        "Ну, привет.\nТы хочешь похудеть, набрать массу или подкачаться?",
        reply_markup=main_menu()
    )
    await callback.answer()