from aiogram import Router
from aiogram.types import Message
from datetime import date, timedelta
from keyboards import get_workout_keyboard, get_main_keyboard, get_workout_by_level
from logger import logger
from db_instance import db

router = Router()

@router.message(lambda message: message.text == "Выполнил")
async def workout_done_handler(message: Message) -> None:
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.full_name

    user = await db.get_user(user_id)
    if not user or not user.get("goal"):
        logger.warning(f"@{username} попытался отметить тренировку без выбора цели")
        await message.answer(
            "Сначала выбери цель через /start",
            reply_markup=get_main_keyboard(user_id, None)
        )
        return

    today = date.today()
    last_date_str = user.get("last_workout_date")
    last_date = date.fromisoformat(last_date_str) if last_date_str else None

    if last_date == today:
        if user.get("gender") == "female":
            logger.info(f"@{username} пыталась отметить тренировку дважды")
            await message.answer(
                "Ты уже отмечала тренировку сегодня! Жди завтрашнего дня. 😴",
                reply_markup=get_workout_keyboard(user_id)
            )
        else:
            logger.info(f"@{username} пытался отметить тренировку дважды")
            await message.answer(
                "Ты уже отмечал тренировку сегодня! Жди завтрашнего дня. 😴",
                reply_markup=get_workout_keyboard(user_id)
            )
        return

    if last_date:
        days_diff = (today - last_date).days
        if days_diff >= 1:
            user["streak"] = 0
            if user.get("gender") == "female":
                logger.info(f"@{username} пропустила день, страйк сброшен")
                await message.answer("Ты пропустила день! Страйк сброшен. 🔄")
            else:
                logger.info(f"@{username} пропустил день, страйк сброшен")
                await message.answer("Ты пропустил день! Страйк сброшен. 🔄")

    user["streak"] = user.get("streak", 0) + 1
    user["last_workout_date"] = today.isoformat()
    user["total_workouts"] = user.get("total_workouts", 0) + 1
    user["workouts_on_level"] = user.get("workouts_on_level", 0) + 1

    if user["level"] == "easy" and user["workouts_on_level"] >= 10:
        user["level"] = "normal"
        user["workouts_on_level"] = 0
        if user.get("gender") == "female":
            await message.answer("🎉 Ты перешла на средний уровень сложности! Горжусь!")
        else:
            await message.answer("🎉 Ты перешёл на средний уровень сложности! Горжусь!")
    elif user["level"] == "normal" and user["workouts_on_level"] >= 50:
        user["level"] = "hard"
        user["workouts_on_level"] = 0
        if user.get("gender") == "female":
            await message.answer("🔥 Ты перешла на тяжёлый уровень сложности! Так держать! \nТеперь в главном меню доступен продвинутый режим!")
        else:
            await message.answer("🔥 Ты перешёл на тяжёлый уровень сложности! Так держать! \nТеперь в главном меню доступен продвинутый режим!")

    await db.save_user(user)

    tomorrow = today + timedelta(days=1)
    new_workout = get_workout_by_level(user["goal"], user["level"])

    logger.info(f"@{username} выполнил тренировку! Страйк: {user['streak']}, уровень: {user['level']}")

    await message.answer(
        f"Молодец! Страйк: {user['streak']} дней\n"
        f"Всего тренировок: {user['total_workouts']}\n\n"
        f"Завтрашнее задание:\n{new_workout}",
        reply_markup=get_workout_keyboard(user_id)
    )

@router.message(lambda message: message.text == "Другое задание")
async def change_workout_handler(message: Message) -> None:
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.full_name

    user = await db.get_user(user_id)
    if not user or not user.get("goal"):
        logger.warning(f"@{username} попытался сменить задание без выбора цели")
        await message.answer(
            "Сначала выбери цель через /start",
            reply_markup=get_main_keyboard(user_id, None)
        )
        return

    new_workout = get_workout_by_level(user["goal"], user["level"])
    logger.info(f"@{username} запросил другое задание")
    await message.answer(
        f"Новое задание:\n{new_workout}",
        reply_markup=get_workout_keyboard(user_id)
    )