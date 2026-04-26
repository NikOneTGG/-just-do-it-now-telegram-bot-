from aiogram import Router
from aiogram.types import Message
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from datetime import date
from config import GYM_WORKOUTS
from db_instance import db
import random

router = Router()

# вспомогательные функции
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

def get_gym_main_keyboard():
    chest_btn = KeyboardButton(text="Грудь")
    back_btn = KeyboardButton(text="Спина")
    legs_btn = KeyboardButton(text="Ноги")
    shoulders_btn = KeyboardButton(text="Плечи")
    arms_btn = KeyboardButton(text="Руки")
    progress_btn = KeyboardButton(text="Мой прогресс")
    leaderboard_btn = KeyboardButton(text="Лидерборд (зал)")
    back_btn_main = KeyboardButton(text="В главное меню")
    
    keyboard_rows = [
        [chest_btn, back_btn],
        [legs_btn, shoulders_btn],
        [arms_btn],
        [progress_btn, leaderboard_btn],
        [back_btn_main]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard_rows, resize_keyboard=True, input_field_placeholder="Выбери группу мышц")

def get_gym_workout_keyboard():
    done_btn = KeyboardButton(text="Готово")
    next_btn = KeyboardButton(text="Следующее")
    finish_btn = KeyboardButton(text="Закончить")
    keyboard_rows = [[done_btn, next_btn], [finish_btn]]
    return ReplyKeyboardMarkup(keyboard=keyboard_rows, resize_keyboard=True, input_field_placeholder="Что делаем?")

ALLOWED_GROUPS = ["Грудь", "Спина", "Ноги", "Плечи", "Руки"]
GROUP_ENGLISH = {
    "Грудь": "chest",
    "Спина": "back",
    "Ноги": "legs",
    "Плечи": "shoulders",
    "Руки": "arms"
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

@router.message(lambda msg: msg.text == "Продвинутый режим")
async def advanced_mode_entry(message: Message):
    user_id = message.from_user.id
    user = await db.get_user(user_id)
    if not user:
        await message.answer("Сначала зарегистрируйся через /start")
        return

    level = user.get("level")
    total = user.get("total_workouts", 0)

    if level and level.startswith("pro"):
        await message.answer(
            "Добро пожаловать в продвинутый режим! Выбери группу мышц:",
            reply_markup=get_gym_main_keyboard()
        )
        return
    if total >= 100:
        await message.answer(
            "Добро пожаловать в продвинутый режим! Выбери группу мышц:",
            reply_markup=get_gym_main_keyboard()
        )
    else:
        remaining = 100 - total
        await message.answer(
            f"Продвинутый режим откроется после 100 тренировок.\nТебе осталось {remaining}.",
            reply_markup=ReplyKeyboardMarkup(keyboard=[], resize_keyboard=True)  # Заглушка, но можно вернуть главное меню
        )

@router.message(lambda msg: msg.text in ALLOWED_GROUPS)
async def process_gym_group(message: Message, state: FSMContext):
    user_id = message.from_user.id
    group_ru = message.text
    group = GROUP_ENGLISH.get(group_ru)
    if not group:
        return

    user = await db.get_user(user_id)
    if not user:
        await message.answer("Сначала зарегистрируйся через /start")
        return

    if "gym_level" not in user:
        user["gym_level"] = "pro1"
        user["gym_workouts_count"] = 0
        user["gym_daily_count"] = 0
        user["gym_last_workout_date"] = None
        await db.save_user(user)

    today = date.today().isoformat()
    if user.get("gym_last_workout_date") != today:
        await db.update_user(user_id,
                             gym_last_workout_date=today,
                             gym_daily_count=0)
        user["gym_last_workout_date"] = today
        user["gym_daily_count"] = 0

    level = user["gym_level"]
    limit = DAILY_LIMITS.get(level, 5)
    if user.get("gym_daily_count", 0) >= limit:
        gender = user.get("gender")
        if gender == "female":
            await message.answer(
                f"Ты уже выполнила лимит на сегодня ({limit} упражнений). Возвращайся завтра!",
                reply_markup=get_gym_main_keyboard()
            )
        else:
            await message.answer(
                f"Ты уже выполнил лимит на сегодня ({limit} упражнений). Возвращайся завтра!",
                reply_markup=get_gym_main_keyboard()
            )
        return

    exercise = get_gym_exercise(group, level)
    await state.update_data(current_group=group)

    await message.answer(
        f"Твоё упражнение:\n{exercise}",
        reply_markup=get_gym_workout_keyboard()
    )

@router.message(lambda msg: msg.text == "Готово")
async def gym_done(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user = await db.get_user(user_id)
    if not user:
        await message.answer("Ошибка: пользователь не найден")
        return

    data = await state.get_data()
    group = data.get("current_group")
    if not group:
        await message.answer(
            "Сначала выбери группу мышц!",
            reply_markup=get_gym_main_keyboard()
        )
        return

    today = date.today().isoformat()
    if user.get("gym_last_workout_date") != today:
        await db.update_user(user_id, gym_last_workout_date=today, gym_daily_count=0)
        user["gym_last_workout_date"] = today
        user["gym_daily_count"] = 0

    level = user["gym_level"]
    limit = DAILY_LIMITS.get(level, 5)
    if user.get("gym_daily_count", 0) >= limit:
        await message.answer(
            f"Лимит на сегодня исчерпан ({limit}).",
            reply_markup=get_gym_main_keyboard()
        )
        return

    new_workouts_count = user.get("gym_workouts_count", 0) + 1
    new_daily_count = user.get("gym_daily_count", 0) + 1
    await db.update_user(user_id,
                         gym_workouts_count=new_workouts_count,
                         gym_daily_count=new_daily_count)
    user["gym_workouts_count"] = new_workouts_count
    user["gym_daily_count"] = new_daily_count

    current_level = user["gym_level"]
    if current_level == "pro1" and new_workouts_count >= GYM_LEVEL_THRESHOLDS["pro1"]:
        await db.update_user(user_id, gym_level="pro2")
        user["gym_level"] = "pro2"
        if user.get("gender") == "female":
            await message.answer(f"🎉 Поздравляю! Ты перешла на уровень {LEVEL_NAMES['pro2']}!")
        else:
            await message.answer(f"🎉 Поздравляю! Ты перешёл на уровень {LEVEL_NAMES['pro2']}!")
    elif current_level == "pro2" and new_workouts_count >= GYM_LEVEL_THRESHOLDS["pro2"]:
        await db.update_user(user_id, gym_level="pro3")
        user["gym_level"] = "pro3"
        if user.get("gender") == "female":
            await message.answer(f"🔥 Ты достигла уровня {LEVEL_NAMES['pro3']}!")
        else:
            await message.answer(f"🔥 Ты достиг уровня {LEVEL_NAMES['pro3']}!")

    new_exercise = get_gym_exercise(group, user["gym_level"])
    await message.answer(
        f"Отлично! Следующее упражнение:\n{new_exercise}",
        reply_markup=get_gym_workout_keyboard()
    )

@router.message(lambda msg: msg.text == "Следующее")
async def gym_next(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user = await db.get_user(user_id)
    if not user:
        await message.answer("Ошибка: пользователь не найден")
        return

    data = await state.get_data()
    group = data.get("current_group")
    if not group:
        await message.answer(
            "Сначала выбери группу мышц!",
            reply_markup=get_gym_main_keyboard()
        )
        return

    today = date.today().isoformat()
    if user.get("gym_last_workout_date") != today:
        await db.update_user(user_id, gym_last_workout_date=today, gym_daily_count=0)
        user["gym_last_workout_date"] = today
        user["gym_daily_count"] = 0

    level = user["gym_level"]
    limit = DAILY_LIMITS.get(level, 5)
    if user.get("gym_daily_count", 0) >= limit:
        await message.answer(
            f"Лимит на сегодня исчерпан ({limit}).",
            reply_markup=get_gym_main_keyboard()
        )
        return

    new_exercise = get_gym_exercise(group, level)
    await message.answer(
        f"Новое упражнение:\n{new_exercise}",
        reply_markup=get_gym_workout_keyboard()
    )

@router.message(lambda msg: msg.text == "Закончить")
async def gym_finish(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user = await db.get_user(user_id)
    if not user:
        await message.answer("Сначала зарегистрируйся")
        return

    await state.clear()
    if user.get("gender") == "female":
        await message.answer(
            "🏁 Сегодня ты потрудилась на славу! Жду тебя завтра.",
            reply_markup=get_gym_main_keyboard()
        )
    else:
        await message.answer(
            "🏁 Сегодня ты потрудился на славу! Жду тебя завтра.",
            reply_markup=get_gym_main_keyboard()
        )

@router.message(lambda msg: msg.text == "Мой прогресс")
async def gym_progress(message: Message):
    user_id = message.from_user.id
    user = await db.get_user(user_id)
    if not user:
        await message.answer("Сначала зарегистрируйся")
        return

    level = user.get("gym_level", "pro1")
    count = user.get("gym_workouts_count", 0)
    daily = user.get("gym_daily_count", 0)
    limit = DAILY_LIMITS.get(level, 5)

    current_name = LEVEL_NAMES.get(level, level)

    if level == "pro1":
        next_level = "pro2"
        need = GYM_LEVEL_THRESHOLDS["pro1"]
        next_name = LEVEL_NAMES.get(next_level, next_level)
        remaining = max(0, need - count)
        text = (
            f"🏋️ ТВОЙ ПРОГРЕСС В ЗАЛЕ\n\n"
            f"Текущий уровень: {current_name}\n"
            f"Всего выполнено упражнений: {count}\n"
            f"До уровня {next_name}: {remaining}\n"
            f"Сегодня выполнено: {daily}/{limit}"
        )
    elif level == "pro2":
        next_level = "pro3"
        need = GYM_LEVEL_THRESHOLDS["pro2"]
        next_name = LEVEL_NAMES.get(next_level, next_level)
        remaining = max(0, need - count)
        text = (
            f"🏋️ ТВОЙ ПРОГРЕСС В ЗАЛЕ\n\n"
            f"Текущий уровень: {current_name}\n"
            f"Всего выполнено упражнений: {count}\n"
            f"До уровня {next_name}: {remaining}\n"
            f"Сегодня выполнено: {daily}/{limit}"
        )
    else:
        text = (
            f"🏋️ ТВОЙ ПРОГРЕСС В ЗАЛЕ\n\n"
            f"Текущий уровень: {current_name}\n"
            f"Всего выполнено упражнений: {count}\n"
            f"{'Ты достигла максимального уровня!' if user.get('gender') == 'female' else 'Ты достиг максимального уровня!'}\n"
            f"Сегодня выполнено: {daily}/{limit}"
        )

    await message.answer(text, reply_markup=get_gym_main_keyboard())

@router.message(lambda msg: msg.text == "Лидерборд (зал)")
async def gym_leaderboard(message: Message):
    users = await db.get_all_users()
    users_with_gym = [u for u in users if u.get("gym_workouts_count", 0) > 0]
    sorted_users = sorted(users_with_gym, key=lambda x: x.get("gym_workouts_count", 0), reverse=True)[:10]

    if not sorted_users:
        await message.answer(
            "В зале пока никто не тренировался.",
            reply_markup=get_gym_main_keyboard()
        )
        return

    text = "🏋️ ЛИДЕРБОРД (ЗАЛ)\n\n"
    for i, u in enumerate(sorted_users, 1):
        name = u.get("first_name") or u.get("username") or str(u.get("user_id"))
        count = u.get("gym_workouts_count", 0)
        text += f"{i}. {name} — {count} тренировок\n"

    await message.answer(text, reply_markup=get_gym_main_keyboard())

@router.message(lambda msg: msg.text == "В главное меню")
async def gym_back_to_main(message: Message, state: FSMContext):
    await state.clear()
    user = await db.get_user(message.from_user.id)
    from inlinekey import main_menu
    await message.answer(
        "Главное меню",
        reply_markup=main_menu()
    )