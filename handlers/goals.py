from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from inlinekey import main_menu, workout_menu, gender_keyboard
from db_instance import db
from logger import logger
from config import WORKOUTS
import random

router = Router()

# выдать случайное задание по цели и уровню
def get_workout_by_level(goal, level):
    if level in ["pro1", "pro2", "pro3"]:
        return random.choice(WORKOUTS[goal]["hard"])
    elif level == "hard":
        combined = WORKOUTS[goal]["normal"] + WORKOUTS[goal]["hard"]
        return random.choice(combined)
    else:
        return random.choice(WORKOUTS[goal][level])

# сброс прогресса при смене цели
def reset_progress(user: dict):
    user["streak"] = 0
    user["total_workouts"] = 0
    user["last_workout_date"] = None
    user["level"] = "easy"
    user["workouts_on_level"] = 0

# команда /start
@router.message(Command("start"))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.full_name

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

# похудение
@router.callback_query(F.data == "lose_weight")
async def lose_weight(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    if not user:
        await callback.message.answer("Сначала запусти бота через /start")
        await callback.answer()
        return

    old_goal = user.get("goal")
    if old_goal and old_goal != "lose_weight":
        reset_progress(user)
        gender = user.get("gender")
        if gender == "female":
            await callback.message.answer("Ты сменила цель. Весь прогресс сброшен.")
        else:
            await callback.message.answer("Ты сменил цель. Весь прогресс сброшен.")

    user["goal"] = "lose_weight"
    workout = get_workout_by_level("lose_weight", user["level"])
    await db.save_user(user)

    await callback.message.delete()
    workout_menu_with_gender = workout_menu(gender=user.get("gender"))
    await callback.message.answer(
        f"Худеть так худеть...\n\nТвоё задание:\n{workout}",
        reply_markup=workout_menu_with_gender
    )
    await callback.answer()

# набор массы
@router.callback_query(F.data == "gain_mass")
async def gain_mass(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    if not user:
        await callback.message.answer("Сначала запусти бота через /start")
        await callback.answer()
        return

    old_goal = user.get("goal")
    if old_goal and old_goal != "gain_mass":
        reset_progress(user)
        gender = user.get("gender")
        if gender == "female":
            await callback.message.answer("Ты сменила цель. Весь прогресс сброшен.")
        else:
            await callback.message.answer("Ты сменил цель. Весь прогресс сброшен.")

    user["goal"] = "gain_mass"
    workout = get_workout_by_level("gain_mass", user["level"])
    await db.save_user(user)

    await callback.message.delete()
    workout_menu_with_gender = workout_menu(gender=user.get("gender"))
    await callback.message.answer(
        f"Набираем массу...\n\nТвоё задание:\n{workout}",
        reply_markup=workout_menu_with_gender
    )
    await callback.answer()

# силовые упражнения(подкачаться)
@router.callback_query(F.data == "fit")
async def fit(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    if not user:
        await callback.message.answer("Сначала запусти бота через /start")
        await callback.answer()
        return

    old_goal = user.get("goal")
    if old_goal and old_goal != "get_fit":
        reset_progress(user)
        gender = user.get("gender")
        if gender == "female":
            await callback.message.answer("Ты сменила цель. Весь прогресс сброшен.")
        else:
            await callback.message.answer("Ты сменил цель. Весь прогресс сброшен.")

    user["goal"] = "get_fit"
    workout = get_workout_by_level("get_fit", user["level"])
    await db.save_user(user)

    await callback.message.delete()
    workout_menu_with_gender = workout_menu(gender=user.get("gender"))
    await callback.message.answer(
        f"Подкачка...\n\nТвоё задание:\n{workout}",
        reply_markup=workout_menu_with_gender
    )
    await callback.answer()

# возврат в главное меню
@router.callback_query(F.data == "main_menu")
async def back_to_main(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer("Главное меню:", reply_markup=main_menu())
    await callback.answer()