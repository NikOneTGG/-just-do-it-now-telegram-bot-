from aiogram import Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from datetime import date
from logger import logger
from keyboards import get_main_keyboard, get_workout_keyboard
from db_instance import db

router = Router()

LEVEL_NAMES = {
    "easy": "Начинающий",
    "normal": "Активный",
    "hard": "Опытный",
    "pro1": "Крепыш",
    "pro2": "Трудяга",
    "pro3": "Мастер"
}

@router.message(lambda message: message.text == "Профиль")
async def profile_handler(message: Message) -> None:
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.full_name

    logger.info(f"@{username} открыл профиль")

    user = await db.get_user(user_id)
    if not user:
        logger.warning(f"@{username} пытался открыть профиль без регистрации")
        await message.answer(
            "Сначала выбери цель через /start",
            reply_markup=get_main_keyboard(user_id, None)
        )
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
        last_date_obj = date.fromisoformat(last_date) if isinstance(last_date, str) else last_date
        days_ago = (date.today() - last_date_obj).days
        last_date_str = last_date_obj.strftime("%d.%m.%Y")
        if days_ago == 0:
            last_text = "Сегодня 🔥"
        elif days_ago == 1:
            last_text = "Вчера"
        else:
            last_text = f"{last_date_str} ({days_ago} дней назад)"
    else:
        last_text = "Ещё не тренировался"

    streak = user.get("streak", 0)
    level_key = user.get("level", "easy")
    level_display = LEVEL_NAMES.get(level_key, level_key)

    response = (
        f"👤 ТВОЙ ПРОФИЛЬ\n\n"
        f"🎯 Цель: {goal_text}\n"
        f"🎯 Уровень: {level_display}\n"
        f"🔥 Страйк: {streak} дней\n"
        f"📊 Всего тренировок: {user.get('total_workouts', 0)}\n"
        f"📅 Последняя тренировка: {last_text}\n"
    )

    total = user.get("total_workouts", 0)
    if total < 100:
        response += f"\n📊 До продвинутого режима: {total}/100 тренировок"
    else:
        response += "\n🏋️ Продвинутый режим разблокирован!"

    achievements = []
    if streak >= 7:
        achievements.append("🔥 7 дней - Новичок")
    if streak >= 30:
        achievements.append("💪 30 дней - Спортсмен")
    if streak >= 100:
        achievements.append("🏆 100 дней - Ветеран")
    if user.get("total_workouts", 0) >= 50:
        achievements.append("📊 50 тренировок - Трудяга")

    if achievements:
        response += "\n\n🏅 ДОСТИЖЕНИЯ:\n"
        for ach in achievements:
            response += f"• {ach}\n"

    keyboard_buttons = []
    if streak > 0:
        reset_btn = KeyboardButton(text="🔄 Обнулить страйк")
        keyboard_buttons.append([reset_btn])

    delete_btn = KeyboardButton(text="🗑 Удалить мои данные")
    keyboard_buttons.append([delete_btn])

    reminder_status = user.get("reminder_enabled", 1)
    reminder_btn_text = "🔔 Отключить напоминания" if reminder_status else "🔕 Включить напоминания"
    reminder_btn = KeyboardButton(text=reminder_btn_text)
    keyboard_buttons.append([reminder_btn])

    back_btn = KeyboardButton(text="◀️ Назад")
    keyboard_buttons.append([back_btn])

    keyboard = ReplyKeyboardMarkup(
        keyboard=keyboard_buttons,
        resize_keyboard=True
    )
    await message.answer(response, reply_markup=keyboard)

@router.message(lambda message: message.text == "🔄 Обнулить страйк")
async def reset_streak_handler(message: Message) -> None:
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.full_name

    user = await db.get_user(user_id)
    if not user:
        logger.warning(f"@{username} пытался обнулить страйк без регистрации")
        await message.answer(
            "Сначала выбери цель через /start",
            reply_markup=get_main_keyboard(user_id, None)
        )
        return

    logger.info(f"@{username} запросил обнуление страйка (текущий: {user.get('streak', 0)})")

    confirm_btn = KeyboardButton(text="✅ Да, обнулить")
    cancel_btn = KeyboardButton(text="❌ Нет, отмена")
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[confirm_btn, cancel_btn]],
        resize_keyboard=True
    )
    await message.answer(
        f"Точно хочешь обнулить страйк? Текущий: {user.get('streak', 0)} дней",
        reply_markup=keyboard
    )

@router.message(lambda message: message.text == "✅ Да, обнулить")
async def confirm_reset_handler(message: Message) -> None:
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.full_name

    user = await db.get_user(user_id)
    if user:
        old_streak = user.get("streak", 0)
        await db.update_user(user_id, streak=0)
        logger.info(f"@{username} обнулил страйк (было: {old_streak})")
        await message.answer(
            "✅ Страйк обнулён. Начинай заново!",
            reply_markup=get_workout_keyboard(user_id)
        )
    else:
        logger.error(f"@{username} ошибка при обнулении страйка")
        await message.answer(
            "Что-то пошло не так",
            reply_markup=get_main_keyboard(user_id, None)
        )

@router.message(lambda message: message.text == "❌ Нет, отмена")
async def cancel_reset_handler(message: Message) -> None:
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.full_name

    logger.info(f"@{username} отменил обнуление страйка")
    await message.answer(
        "Ок, возвращаемся",
        reply_markup=get_workout_keyboard(user_id)
    )

@router.message(lambda message: message.text == "🗑 Удалить мои данные")
async def delete_account_handler(message: Message):
    user_id = message.from_user.id
    user = await db.get_user(user_id)
    if not user:
        await message.answer("Вы не зарегистрированы.")
        return
    confirm_btn = KeyboardButton(text="✅ Да, удалить")
    cancel_btn = KeyboardButton(text="❌ Нет, отмена")
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[confirm_btn, cancel_btn]],
        resize_keyboard=True
    )
    await message.answer(
        "⚠️ ВНИМАНИЕ!\n"
        "Все ваши данные (статистика, уровень, прогресс) будут удалены без возможности восстановления.\n"
        "Вы уверены?",
        reply_markup=keyboard
    )

@router.message(lambda message: message.text == "✅ Да, удалить")
async def confirm_delete_account(message: Message):
    user_id = message.from_user.id
    await db.delete_user(user_id)
    await message.answer(
        "Ваши данные удалены.\n"
        "Чтобы начать заново, нажмите /start",
        reply_markup=get_main_keyboard(user_id, None)
    )

@router.message(lambda message: message.text == "❌ Нет, отмена")
async def cancel_delete_account(message: Message):
    user_id = message.from_user.id
    await message.answer(
        "Удаление отменено.",
        reply_markup=get_workout_keyboard(user_id)
    )

@router.message(lambda message: message.text in ["🔔 Отключить напоминания", "🔕 Включить напоминания"])
async def toggle_reminder(message: Message):
    user_id = message.from_user.id
    user = await db.get_user(user_id)
    if not user:
        await message.answer("Сначала зарегистрируйся через /start")
        return
    current = user.get("reminder_enabled", 1)
    new_value = 0 if current else 1
    await db.update_user(user_id, reminder_enabled=new_value)
    await message.answer("Напоминания отключены." if new_value == 0 else "Напоминания включены.")