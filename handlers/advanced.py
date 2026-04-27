from aiogram import Router, F
from aiogram.types import CallbackQuery
from datetime import date
from config import GYM_WORKOUTS
from db_instance import db
from inlinekey import gym_groups_keyboard, gym_workout_keyboard, gym_back_keyboard
import random
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

router = Router()

class GymState(StatesGroup):
    current_group = State()

GROUP_NAMES = {
    "chest": "Грудь",
    "back": "Спина",
    "legs": "Ноги",
    "shoulders": "Плечи",
    "arms": "Руки"
}

DAILY_LIMITS = {
    "pro1": 5,
    "pro2": 7,
    "pro3": 10
}

GYM_LEVEL_THRESHOLDS = {
    "pro1": 50,
    "pro2": 150
}

LEVEL_NAMES = {
    "pro1": "Железный новичок",
    "pro2": "Железный трудяга",
    "pro3": "Железный мастер"
}

def get_gym_exercise(muscle_group: str, level: str) -> str:
    if level == "pro1":
        return random.choice(GYM_WORKOUTS[muscle_group]["pro1"])
    elif level == "pro2":
        combined = GYM_WORKOUTS[muscle_group]["pro1"] + GYM_WORKOUTS[muscle_group]["pro2"]
        return random.choice(combined)
    elif level == "pro3":
        combined = (GYM_WORKOUTS[muscle_group]["pro1"] +
                    GYM_WORKOUTS[muscle_group]["pro2"] +
                    GYM_WORKOUTS[muscle_group]["pro3"])
        return random.choice(combined)
    else:
        return random.choice(GYM_WORKOUTS[muscle_group]["pro1"])

@router.callback_query(F.data == "advanced_mode")
async def advanced_mode_entry(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    if not user:
        await callback.message.answer("Сначала зарегистрируйся через /start")
        await callback.answer()
        return
    total = user.get("total_workouts", 0)
    level = user.get("level")
    if total >= 100 or (level and level.startswith("pro")):
        await callback.message.delete()
        await callback.message.answer("Продвинутый режим\nВыбери группу мышц:", reply_markup=gym_groups_keyboard())
    else:
        remaining = 100 - total
        await callback.answer(f"Продвинутый режим откроется после 100 тренировок. Осталось {remaining}.", show_alert=True)
    await callback.answer()

@router.callback_query(F.data == "gym_progress")
async def gym_progress(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    if not user:
        await callback.answer("Сначала зарегистрируйся", show_alert=True)
        return
    level = user.get("gym_level", "pro1")
    count = user.get("gym_workouts_count", 0)
    daily = user.get("gym_daily_count", 0)
    limit = DAILY_LIMITS.get(level, 5)
    current_name = LEVEL_NAMES.get(level, level)
    if level == "pro1":
        need = GYM_LEVEL_THRESHOLDS["pro1"]
        remaining = max(0, need - count)
        text = f"Твой прогресс в зале:\n\nУровень: {current_name}\nВыполнено: {count}\nДо {LEVEL_NAMES['pro2']}: {remaining}\nСегодня: {daily}/{limit}"
    elif level == "pro2":
        need = GYM_LEVEL_THRESHOLDS["pro2"]
        remaining = max(0, need - count)
        text = f"Твой прогресс в зале:\n\nУровень: {current_name}\nВыполнено: {count}\nДо {LEVEL_NAMES['pro3']}: {remaining}\nСегодня: {daily}/{limit}"
    else:
        text = f"Твой прогресс в зале:\n\nУровень: {current_name}\nВыполнено: {count}\nМаксимальный уровень.\nСегодня: {daily}/{limit}"
    await callback.message.delete()
    await callback.message.answer(text, reply_markup=gym_back_keyboard())
    await callback.answer()

@router.callback_query(F.data == "gym_leaderboard")
async def gym_leaderboard(callback: CallbackQuery):
    users = await db.get_all_users()
    active = [u for u in users if u.get("gym_workouts_count", 0) > 0]
    sorted_users = sorted(active, key=lambda x: x.get("gym_workouts_count", 0), reverse=True)[:10]
    if not sorted_users:
        text = "В зале пока никто не тренировался."
    else:
        text = "Лидерборд зала\n\n"
        for i, u in enumerate(sorted_users, 1):
            name = u.get("first_name") or u.get("username") or "Аноним"
            count = u.get("gym_workouts_count", 0)
            text += f"{i}. {name} — {count} тренировок\n"
    await callback.message.delete()
    await callback.message.answer(text, reply_markup=gym_back_keyboard())
    await callback.answer()

@router.callback_query(F.data == "gym_done")
async def gym_done(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    group = data.get("current_group")
    if not group:
        await callback.answer("Сначала выбери группу мышц.", show_alert=True)
        return
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    if not user:
        await callback.answer("Ошибка", show_alert=True)
        return
    today = date.today().isoformat()
    if user.get("gym_last_workout_date") != today:
        user["gym_last_workout_date"] = today
        user["gym_daily_count"] = 0
        await db.update_user(user_id, gym_last_workout_date=today, gym_daily_count=0)
    level = user["gym_level"]
    limit = DAILY_LIMITS.get(level, 5)
    if user.get("gym_daily_count", 0) >= limit:
        await callback.answer("Лимит на сегодня исчерпан.", show_alert=True)
        return
    new_count = user.get("gym_workouts_count", 0) + 1
    new_daily = user.get("gym_daily_count", 0) + 1
    await db.update_user(user_id, gym_workouts_count=new_count, gym_daily_count=new_daily)
    if user["gym_level"] == "pro1" and new_count >= GYM_LEVEL_THRESHOLDS["pro1"]:
        await db.update_user(user_id, gym_level="pro2")
        user["gym_level"] = "pro2"
        await callback.message.answer(f"Поздравляю! Ты перешёл на уровень {LEVEL_NAMES['pro2']}.")
    elif user["gym_level"] == "pro2" and new_count >= GYM_LEVEL_THRESHOLDS["pro2"]:
        await db.update_user(user_id, gym_level="pro3")
        user["gym_level"] = "pro3"
        await callback.message.answer(f"Поздравляю! Ты достиг уровня {LEVEL_NAMES['pro3']}.")
    new_exercise = get_gym_exercise(group, user["gym_level"])
    await callback.message.delete()
    await callback.message.answer(f"Молодец! Следующее упражнение:\n{new_exercise}", reply_markup=gym_workout_keyboard())
    await callback.answer()

@router.callback_query(F.data == "gym_next")
async def gym_next(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    group = data.get("current_group")
    if not group:
        await callback.answer("Сначала выбери группу мышц.", show_alert=True)
        return
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    if not user:
        await callback.answer("Ошибка", show_alert=True)
        return
    today = date.today().isoformat()
    if user.get("gym_last_workout_date") != today:
        user["gym_last_workout_date"] = today
        user["gym_daily_count"] = 0
        await db.update_user(user_id, gym_last_workout_date=today, gym_daily_count=0)
    level = user["gym_level"]
    limit = DAILY_LIMITS.get(level, 5)
    if user.get("gym_daily_count", 0) >= limit:
        await callback.answer("Лимит на сегодня исчерпан.", show_alert=True)
        return
    new_exercise = get_gym_exercise(group, level)
    await callback.message.delete()
    await callback.message.answer(f"Следующее упражнение:\n{new_exercise}", reply_markup=gym_workout_keyboard())
    await callback.answer()

@router.callback_query(F.data == "gym_finish")
async def gym_finish(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    await callback.message.answer("Тренировка завершена. Жду тебя завтра.", reply_markup=gym_groups_keyboard())
    await callback.answer()

@router.callback_query(F.data == "gym_back")
async def gym_back(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    await callback.message.answer("Выбери группу мышц:", reply_markup=gym_groups_keyboard())
    await callback.answer()

# общий обработчик для выбора группы мышц
@router.callback_query(F.data.startswith("gym_"))
async def gym_group_selected(callback: CallbackQuery, state: FSMContext):
    group = callback.data.split("_")[1]
    if group not in GROUP_NAMES:
        await callback.answer()
        return
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    if not user:
        await callback.message.answer("Сначала зарегистрируйся через /start")
        await callback.answer()
        return
    if "gym_level" not in user:
        user["gym_level"] = "pro1"
        user["gym_workouts_count"] = 0
        user["gym_daily_count"] = 0
        user["gym_last_workout_date"] = None
        await db.save_user(user)
    today = date.today().isoformat()
    if user.get("gym_last_workout_date") != today:
        user["gym_last_workout_date"] = today
        user["gym_daily_count"] = 0
        await db.update_user(user_id, gym_last_workout_date=today, gym_daily_count=0)
    level = user["gym_level"]
    limit = DAILY_LIMITS.get(level, 5)
    if user.get("gym_daily_count", 0) >= limit:
        gender = user.get("gender")
        answer_text = f"Ты уже выполнил{'' if gender != 'female' else 'а'} лимит на сегодня ({limit} упражнений). Возвращайся завтра."
        await callback.answer(answer_text, show_alert=True)
        return
    await state.update_data(current_group=group)
    exercise = get_gym_exercise(group, level)
    await callback.message.delete()
    await callback.message.answer(f"Твоё упражнение ({GROUP_NAMES[group]}):\n{exercise}", reply_markup=gym_workout_keyboard())
    await callback.answer()