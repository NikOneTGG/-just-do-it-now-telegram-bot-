from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import date
from inlinekey import workout_menu, main_menu, profile_menu
from db_instance import db
from logger import logger

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

# цели
    goal_names = {
        "lose_weight": "Похудение",
        "gain_mass": "Набор массы",
        "get_fit": "Подкачка",
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
        f"ТВОЙ ПРОФИЛЬ\n\n"
        f"Цель: {goal_text}\n"
        f"Уровень: {LEVEL_NAMES.get(user.get('level', 'easy'))}\n"
        f"Страйк: {user.get('streak', 0)} дней\n"
        f"Всего тренировок: {user.get('total_workouts', 0)}\n"
        f"Последняя тренировка: {last_text}\n"
    )

    await callback.message.delete()
    await callback.message.answer(response, reply_markup=profile_menu())
    await callback.answer()

# сброс страйка
@router.callback_query(F.data == "reset_streak")
async def reset_streak_request(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    if not user:
        await callback.message.answer("Сначала зарегистрируйся через /start")
        await callback.answer()
        return
    
    confirm_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Да, обнулить", callback_data="confirm_reset_streak"),
         InlineKeyboardButton(text="Нет, отмена", callback_data="cancel_reset_streak")]
    ])
    await callback.message.edit_text(
        f"Точно хочешь обнулить страйк? Текущий: {user.get('streak', 0)}",
        reply_markup=confirm_keyboard
    )
    await callback.answer()

# подтверждение сброса страйка
@router.callback_query(F.data == "confirm_reset_streak")
async def reset_streak_request(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    if user:
        old_streak = user.get("streak", 0)
        await db.update_user(user_id, streak=0)
        logger.info(f"Пользователь {user_id} обнулил страйк (было {old_streak})")
        await callback.message.edit_text("Страйк обнулён. Начинай заново!", reply_markup=main_menu())
    else:
        await callback.message.edit_text("Что-то пошло не так", reply_markup=main_menu())
    await callback.answer()

# отмена сброса страйка
@router.callback_query(F.data == "cancel_reset_streak")
async def cancel_reset_streak(callback: CallbackQuery):
    await callback.message.edit_text("Отмена", reply_markup=profile_menu())
    await callback.answer()

# удаление профиля
@router.callback_query(F.data == "delete_account")
async def delete_account_request(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = await db.get_user
    if not user:
        await callback.message.answer("Сначала зарегистрируйся через /start")
        await callback.answer()
        return

    confirm_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Да, удалить", callback_data="confirm_delete_account"),
         InlineKeyboardButton(text="Нет, отмена", callback_data="cancel_delete_account")]
    ])
    await callback.message.edit_text(
        "Все ваши данные будут удалены без возможности восстановления\nВы уверены?",
        reply_markup=confirm_keyboard
    )
    await callback.answer()

# подтверждение удаления профиля
@router.callback_query(F.data == "confirm_delete_account")
async def confirm_delete_account(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    logger.info(f"Пользователь {user_id} удалил свой аккаунт")
    await callback.message.edit_text(
        "Ваши данные были удалены\nЧтобы начать заново, напишите /start",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Начать", callback_data="restart")]
        ])
    )
    await callback.answer()
# отмена удаления профиля
@router.callback_query(F.data == "cancel_delete_account")
async def cancel_delete_account(callback: CallbackQuery):
    await callback.message.edit_text("Отменено", reply_markup=profile_menu())
    await callback.answer()

