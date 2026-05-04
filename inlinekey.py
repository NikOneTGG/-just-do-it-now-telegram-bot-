from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu():
    buttons = [
        [
            InlineKeyboardButton(text="Похудеть", callback_data="lose_weight"),
            InlineKeyboardButton(text="Набрать массу", callback_data="gain_mass")
        ],
        [
            InlineKeyboardButton(text="Подкачаться", callback_data="fit"),
            InlineKeyboardButton(text="Профиль", callback_data="profile")
        ],
        [
            InlineKeyboardButton(text="Лидерборд", callback_data="leaderboard"),
            InlineKeyboardButton(text="Продвинутый режим", callback_data="advanced_mode")
        ],
        [
            InlineKeyboardButton(text="Питание", callback_data="nutrition")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def workout_menu(gender=None):
    done_text = "Выполнил" if gender != "female" else "Выполнила"
    buttons = [
        [
            InlineKeyboardButton(text=done_text, callback_data="workout_done"),
            InlineKeyboardButton(text="Другое задание", callback_data="workout_change")
        ],
        [
            InlineKeyboardButton(text="Профиль", callback_data="profile"),
            InlineKeyboardButton(text="В главное меню", callback_data="main_menu")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def leaderboard_menu():
    buttons = [
        [InlineKeyboardButton(text="В главное меню", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def gender_keyboard():
    buttons = [
        [
            InlineKeyboardButton(text="Мужской", callback_data="gender_male"),
            InlineKeyboardButton(text="Женский", callback_data="gender_female")
        ]
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

def gym_groups_keyboard():
    buttons = [
        [
            InlineKeyboardButton(text="Грудь", callback_data="gym_chest"),
            InlineKeyboardButton(text="Спина", callback_data="gym_back")
        ],
        [
            InlineKeyboardButton(text="Ноги", callback_data="gym_legs"),
            InlineKeyboardButton(text="Плечи", callback_data="gym_shoulders")
        ],
        [
            InlineKeyboardButton(text="Руки", callback_data="gym_arms")
        ],
        [
            InlineKeyboardButton(text="Мой прогресс", callback_data="gym_progress"),
            InlineKeyboardButton(text="Лидерборд зала", callback_data="gym_leaderboard")
        ],
        [
            InlineKeyboardButton(text="В главное меню", callback_data="main_menu")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def gym_workout_keyboard():
    buttons = [
        [
            InlineKeyboardButton(text="Выполнил", callback_data="gym_done"),
            InlineKeyboardButton(text="Следующее", callback_data="gym_next")
        ],
        [InlineKeyboardButton(text="Закончить", callback_data="gym_finish")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def gym_back_keyboard():
    buttons = [[InlineKeyboardButton(text="Назад", callback_data="gym_back")]]
    return InlineKeyboardMarkup(inline_keyboard=buttons)