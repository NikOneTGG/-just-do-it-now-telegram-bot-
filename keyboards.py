import random
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from config import ADMIN_IDS, WORKOUTS, GYM_WORKOUTS

def get_main_keyboard(user_id=None, user_level=None):
    lose_btn = KeyboardButton(text="Похудеть🏃‍♂️‍➡️")
    gain_btn = KeyboardButton(text="Набрать массу🍗")
    fit_btn = KeyboardButton(text="Подкачаться🏋️‍♂️")
    profile_btn = KeyboardButton(text="Профиль👤")
    leaderboard_btn = KeyboardButton(text="Лидерборд🏆")
    
    keyboard_rows = [
        [lose_btn, gain_btn],
        [fit_btn, profile_btn],
        [leaderboard_btn]
    ]
    
    if user_id and user_level in ["hard", "pro1", "pro2", "pro3"]:
        advanced_btn = KeyboardButton(text="Продвинутый режим")
        keyboard_rows.append([advanced_btn])

    # Кнопка "О нас" для всех пользователей
    about_btn = KeyboardButton(text="О нас🗣")
    keyboard_rows.append([about_btn])
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=keyboard_rows,
        resize_keyboard=True,
        input_field_placeholder="Выбери свою цель"
    )
    return keyboard

def get_workout_keyboard(user_id=None):
    done_btn = KeyboardButton(text="Выполнил")
    change_btn = KeyboardButton(text="Другое задание")
    profile_btn = KeyboardButton(text="Профиль")
    main_menu_btn = KeyboardButton(text="В главное меню")
    
    keyboard_rows = [
        [done_btn, change_btn],
        [profile_btn, main_menu_btn]
    ]

    # Кнопка "О нас" для всех пользователей
    about_btn = KeyboardButton(text="О нас")
    keyboard_rows.append([about_btn])
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=keyboard_rows,
        resize_keyboard=True,
        input_field_placeholder="Что делаем?"
    )
    return keyboard

def get_workout_by_level(goal, level):
    if level in ["pro1", "pro2", "pro3"]:
        return random.choice(WORKOUTS[goal]["hard"])
    elif level == "hard":
        combined = WORKOUTS[goal]["normal"] + WORKOUTS[goal]["hard"]
        return random.choice(combined)
    else:
        return random.choice(WORKOUTS[goal][level])

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
    return ReplyKeyboardMarkup(
        keyboard=keyboard_rows,
        resize_keyboard=True,
        input_field_placeholder="Выбери группу мышц"
    )

def get_gym_workout_keyboard():
    done_btn = KeyboardButton(text="Готово")
    next_btn = KeyboardButton(text="Следующее")
    finish_btn = KeyboardButton(text="Закончить")
    keyboard_rows = [
        [done_btn, next_btn],
        [finish_btn]
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard_rows,
        resize_keyboard=True,
        input_field_placeholder="Что делаем?"
    )