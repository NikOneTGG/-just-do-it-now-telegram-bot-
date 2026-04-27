from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu():
    buttons = [
        [InlineKeyboardButton(text="Похудеть", callback_data="goal_lose")],
        [InlineKeyboardButton(text="Набрать массу", callback_data="goal_gain")],
        [InlineKeyboardButton(text="Подкачаться", callback_data="goal_fit")],
        [InlineKeyboardButton(text="Профиль", callback_data="profile")],
        [InlineKeyboardButton(text="Лидерборд", callback_data="leaderboard")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def workout_menu():
    buttons = [
        [InlineKeyboardButton(text="Выполнил", callback_data="workout_done"),
         InlineKeyboardButton(text="Другое задание", callback_data="workout_change")],
        [InlineKeyboardButton(text="Профиль", callback_data="profile"),
         InlineKeyboardButton(text="В главное меню", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def gender_keyboard():
    buttons = [
        [InlineKeyboardButton(text="Мужской", callback_data="gender_male"),
         InlineKeyboardButton(text="Женский", callback_data="gender_female")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def profile_menu():
    buttons = [
        [InlineKeyboardButton(text="Обнулить страйк", callback_data="reset_streak")],
        [InlineKeyboardButton(text="Удалить мои данные", callback_data="delete_account")],
        [InlineKeyboardButton(text="Напоминания", callback_data="toggle_reminder")],
        [InlineKeyboardButton(text="В главное меню", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)