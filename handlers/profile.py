from aiogram import Router, F
from aiogram.types import CallbackQuery
from datetime import date
from inlinekey import workout_menu
from db_instance import db

router = Router()

# названия уровней для красивого отображения
LEVEL_NAMES = {
    "easy": "Начинающий",
    "normal": "Активный",
    "hard": "Опытный",
    "pro1": "Крепыш",
    "pro2": "Трудяга",
    "pro3": "Мастер"
}

# профиль пользователя
@router.callback_query(F.data == "profile")
async def profile_handler(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    if not user:
        await callback.message.answer("Сначала зарегистрируйся через /start")
        await callback.answer()
        return

    goal_names = {
        "lose_weight": "Похудение 🔥",
        "gain_mass": "Набор массы 💪",
        "get_fit": "Подкачка 🏋️",
        None: "Не выбрана"
    }
    goal_text = goal_names.get(user.get("goal"), "Не выбрана")

    last_date = user.get("last_workout_date")
    if last_date:
        days_ago = (date.today() - date.fromisoformat(last_date)).days
        last_text = f"{days_ago} дней назад"
    else:
        last_text = "Ещё не тренировался"

    response = (
        f"👤 ТВОЙ ПРОФИЛЬ\n\n"
        f"🎯 Цель: {goal_text}\n"
        f"🎯 Уровень: {LEVEL_NAMES.get(user.get('level', 'easy'))}\n"
        f"🔥 Страйк: {user.get('streak', 0)} дней\n"
        f"📊 Всего тренировок: {user.get('total_workouts', 0)}\n"
        f"📅 Последняя тренировка: {last_text}\n"
    )

    await callback.message.delete()
    await callback.message.answer(response, reply_markup=workout_menu())
    await callback.answer()