from aiogram import Router, F
from aiogram.types import CallbackQuery
from datetime import date, timedelta
from inlinekey import workout_menu
from handlers.goals import get_workout_by_level
from db_instance import db
from logger import logger

router = Router()

# выполнение тренировки
@router.callback_query(F.data == "workout_done")
async def workout_done(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    if not user or not user.get("goal"):
        await callback.message.answer("Сначала выбери цель через /start")
        await callback.answer()
        return

    gender = user.get("gender")
    today = date.today()
    last_date_str = user.get("last_workout_date")
    last_date = date.fromisoformat(last_date_str) if last_date_str else None

    if last_date == today:
        if gender == "female":
            await callback.message.answer("Ты уже отмечала тренировку сегодня! Жди завтрашнего дня. 😴")
        else:
            await callback.message.answer("Ты уже отмечал тренировку сегодня! Жди завтрашнего дня. 😴")
        await callback.answer()
        return

    if last_date:
        days_diff = (today - last_date).days
        if days_diff >= 1:
            user["streak"] = 0
            if gender == "female":
                await callback.message.answer("Ты пропустила день! Страйк сброшен. 🔄")
            else:
                await callback.message.answer("Ты пропустил день! Страйк сброшен. 🔄")

    user["streak"] = user.get("streak", 0) + 1
    user["last_workout_date"] = today.isoformat()
    user["total_workouts"] = user.get("total_workouts", 0) + 1
    user["workouts_on_level"] = user.get("workouts_on_level", 0) + 1

    # повышение уровня
    if user["level"] == "easy" and user["workouts_on_level"] >= 10:
        user["level"] = "normal"
        user["workouts_on_level"] = 0
        if gender == "female":
            await callback.message.answer("🎉 Ты перешла на средний уровень! Горжусь!")
        else:
            await callback.message.answer("🎉 Ты перешёл на средний уровень! Горжусь!")
    elif user["level"] == "normal" and user["workouts_on_level"] >= 50:
        user["level"] = "hard"
        user["workouts_on_level"] = 0
        if gender == "female":
            await callback.message.answer("🔥 Ты перешла на тяжёлый уровень! Так держать! Теперь доступен продвинутый режим.")
        else:
            await callback.message.answer("🔥 Ты перешёл на тяжёлый уровень! Так держать! Теперь доступен продвинутый режим.")

    await db.save_user(user)

    new_workout = get_workout_by_level(user["goal"], user["level"])

    await callback.message.delete()
    await callback.message.answer(
        f"Молодец! Страйк: {user['streak']} дней\n"
        f"Всего тренировок: {user['total_workouts']}\n\n"
        f"Завтрашнее задание:\n{new_workout}",
        reply_markup=workout_menu()
    )
    await callback.answer()

# смена задания
@router.callback_query(F.data == "workout_change")
async def workout_change(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    if not user or not user.get("goal"):
        await callback.message.answer("Сначала выбери цель через /start")
        await callback.answer()
        return

    new_workout = get_workout_by_level(user["goal"], user["level"])

    await callback.message.delete()
    await callback.message.answer(
        f"Новое задание:\n{new_workout}",
        reply_markup=workout_menu()
    )
    await callback.answer()