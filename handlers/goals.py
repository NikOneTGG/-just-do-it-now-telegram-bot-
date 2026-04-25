from aiogram import Router
from aiogram.types import Message
from keyboards import get_workout_keyboard, get_workout_by_level
from logger import logger
from db_instance import db

router = Router()

def reset_progress(user: dict):
    user["streak"] = 0
    user["total_workouts"] = 0
    user["last_workout_date"] = None
    user["level"] = "easy"
    user["workouts_on_level"] = 0

@router.message(lambda message: message.text == "Похудеть")
async def lose_weight_handler(message: Message) -> None:
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

    old_goal = user.get("goal")
    if old_goal and old_goal != "lose_weight":
        reset_progress(user)
        if user.get("gender") == "female":
            await message.answer("Ты сменила цель. Весь прогресс по предыдущей цели сброшен. Начинаем с чистого листа!")
        else:
            await message.answer("Ты сменил цель. Весь прогресс по предыдущей цели сброшен. Начинаем с чистого листа!")
        await db.save_user(user)

    user["goal"] = "lose_weight"
    workout = get_workout_by_level("lose_weight", user["level"])
    logger.info(f"@{username} выбрал цель: Похудеть")
    await db.save_user(user)

    await message.answer(
        f"Худеть так худеть, отныне будем питаться правильно и много тренироваться.\n\n"
        f"Твоё задание на сегодня:\n{workout}",
        reply_markup=get_workout_keyboard(user_id)
    )

@router.message(lambda message: message.text == "Набрать массу")
async def gain_mass_handler(message: Message) -> None:
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

    old_goal = user.get("goal")
    if old_goal and old_goal != "gain_mass":
        reset_progress(user)
        if user.get("gender") == "female":
            await message.answer("Ты сменила цель. Весь прогресс по предыдущей цели сброшен. Начинаем с чистого листа!")
        else:
            await message.answer("Ты сменил цель. Весь прогресс по предыдущей цели сброшен. Начинаем с чистого листа!")
        await db.save_user(user)

    user["goal"] = "gain_mass"
    workout = get_workout_by_level("gain_mass", user["level"])
    logger.info(f"@{username} выбрал цель: Набрать массу")
    await db.save_user(user)

    await message.answer(
        f"Набираем массу! Больше белка и тяжелых тренировок.\n\n"
        f"Твоё задание на сегодня:\n{workout}",
        reply_markup=get_workout_keyboard(user_id)
    )

@router.message(lambda message: message.text == "Подкачаться")
async def pump_up_handler(message: Message) -> None:
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

    old_goal = user.get("goal")
    if old_goal and old_goal != "get_fit":
        reset_progress(user)
        if user.get("gender") == "female":
            await message.answer("Ты сменила цель. Весь прогресс по предыдущей цели сброшен. Начинаем с чистого листа!")
        else:
            await message.answer("Ты сменил цель. Весь прогресс по предыдущей цели сброшен. Начинаем с чистого листа!")
        await db.save_user(user)

    user["goal"] = "get_fit"
    workout = get_workout_by_level("get_fit", user["level"])
    logger.info(f"@{username} выбрал цель: Подкачаться")
    await db.save_user(user)

    await message.answer(
        f"Подкачаться - это по нашему! Рельеф и тонус.\n\n"
        f"Твоё задание на сегодня:\n{workout}",
        reply_markup=get_workout_keyboard(user_id)
    )