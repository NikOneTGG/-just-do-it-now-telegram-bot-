from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from config import MEALS
from db_instance import db
import random

router = Router()

#клавиши для питания
def nutrition_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Завтрак", callback_data="meal_breakfast"),
         InlineKeyboardButton(text="Обед", callback_data="meal_lunch")],
        [InlineKeyboardButton(text="Ужин", callback_data="meal_dinner"),
         InlineKeyboardButton(text="Перекус", callback_data="meal_snack")],
        [InlineKeyboardButton(text="Назад", callback_data="main_menu")]
    ])

#сообщение о выборе времени приёма пищи
@router.callback_query(F.data == "nutrition")
async def nutrition_menu(callback: CallbackQuery):
    await callback.message.edit_text("Выбери приём пищи:", reply_markup=nutrition_keyboard())
    await callback.answer()

#обработка и выдача питания
@router.callback_query(F.data.startswith("meal_"))
async def send_meal(callback: CallbackQuery):
    meal_type = callback.data.split("_")[1]
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    goal = user.get("goal", "get_fit")
    meals = MEALS.get(goal, MEALS["get_fit"])
    options = meals.get(meal_type, [])
    if options:
        meal = random.choice(options)
        text = f"{meal_type.capitalize()}:\n{meal}"
    else:
        text = "Нет рекомендаций."
    await callback.message.edit_text(text, reply_markup=nutrition_keyboard())
    await callback.answer()