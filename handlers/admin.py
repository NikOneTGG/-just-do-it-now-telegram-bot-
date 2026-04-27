from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import FSInputFile
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramRetryAfter
from aiogram.fsm.state import StatesGroup, State
from config import ADMIN_IDS, GYM_WORKOUTS
from logger import logger
from aiogram.exceptions import TelegramBadRequest
import os
import asyncio
import random
from datetime import date
from db_instance import db

router = Router()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_PATH = os.path.join(BASE_DIR, "logs", "bot.log")

if isinstance(ADMIN_IDS, int):
    ADMIN_LIST = [ADMIN_IDS]
else:
    ADMIN_LIST = list(ADMIN_IDS)

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

# обработчик кнопки О нас
@router.message(lambda message: message.text == "О нас")
async def about_handler(message: Message):
    user_id = message.from_user.id
    if user_id in ADMIN_LIST:
        await message.answer("аварийная остановка...")
        await message.bot.session.close()
        raise SystemExit
    else:
        await message.answer("ТГК:\nhttps://t.me/JustDoItNEWS\nПоддержка: @JDINOWBOTSUPPORT")

# FSM состояния
class SetLevelState(StatesGroup):
    waiting_for_user_id = State()
    waiting_for_level = State()

class BoostState(StatesGroup):
    waiting_for_user_id = State()
    waiting_for_value = State()

class BroadcastState(StatesGroup):
    waiting_for_message = State()

class DeleteUserState(StatesGroup):
    waiting_for_user_id = State()

# клавиатуры админки
def admin_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton(text="Установить уровень", callback_data="admin_setlevel")],
        [InlineKeyboardButton(text="Выдать pro3", callback_data="admin_grant_pro3")],
        [InlineKeyboardButton(text="Накрутка страйка", callback_data="admin_boost")],
        [InlineKeyboardButton(text="Логи", callback_data="admin_logs")],
        [InlineKeyboardButton(text="Тест напоминалки", callback_data="admin_test_remind")],
        [InlineKeyboardButton(text="Очистить лог-файл", callback_data="admin_clear_logs")],
        [InlineKeyboardButton(text="Рассылка", callback_data="admin_broadcast")],
        [InlineKeyboardButton(text="Закрыть", callback_data="admin_close")],
        [InlineKeyboardButton(text="Удалить пользователя", callback_data="admin_delete_user")]
    ])

def back_button():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Назад", callback_data="admin_back")]
    ])

def get_id_selection_keyboard(action: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👤 Себе", callback_data=f"admin_{action}_self")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_back")]
    ])

# команды
@router.message(Command("admin"))
async def admin_panel(message: Message):
    if message.from_user.id not in ADMIN_LIST:
        return
    await message.answer("Админ-панель", reply_markup=admin_keyboard())

@router.message(Command("test_gym"))
async def test_gym(message: Message):
    if message.from_user.id not in ADMIN_LIST:
        return
    group = random.choice(["chest", "back", "legs", "shoulders", "arms"])
    level = random.choice(["pro1", "pro2", "pro3"])
    exercise = get_gym_exercise(group, level)
    await message.answer(f"Тест: {group} / {level}\n{exercise}")

# выдать pro3 
@router.callback_query(F.data == "admin_grant_pro3")
async def admin_grant_pro3(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_LIST:
        return
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    if not user:
        await callback.message.edit_text("Сначала зарегистрируйся через /start")
        await callback.answer()
        return
    await db.update_user(user_id, level="pro3", gym_level="pro3", gym_workouts_count=30)
    logger.info(f"Админ {user_id} выдал себе pro3")
    await callback.message.edit_text("✅ Ты получил уровень pro3. Можешь тестировать.", reply_markup=back_button())
    await callback.answer()

# установка уровня
@router.callback_query(F.data == "admin_setlevel")
async def admin_setlevel_start(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_LIST:
        return
    await callback.message.delete()
    await callback.message.answer(
        "Введи ID пользователя или нажми кнопку 'Себе':",
        reply_markup=get_id_selection_keyboard("setlevel")
    )
    await state.set_state(SetLevelState.waiting_for_user_id)
    await callback.answer()

@router.callback_query(F.data == "admin_setlevel_self")
async def admin_setlevel_self(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_LIST:
        return
    user_id = callback.from_user.id
    if not await db.get_user(user_id):
        await callback.message.edit_text("Сначала зарегистрируйся через /start")
        await callback.answer()
        return
    await state.update_data(target_user_id=user_id)
    await callback.message.edit_text("Теперь введи уровень: easy / normal / hard / pro1 / pro2 / pro3")
    await state.set_state(SetLevelState.waiting_for_level)
    await callback.answer()

@router.message(SetLevelState.waiting_for_user_id)
async def process_user_id(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_LIST:
        return
    try:
        user_id = int(message.text.strip())
    except ValueError:
        await message.answer("Ошибка: ID должен быть числом.")
        return
    if not await db.get_user(user_id):
        await message.answer("Ошибка: пользователь не найден.")
        return
    await state.update_data(target_user_id=user_id)
    await message.answer("Теперь введи уровень: easy / normal / hard / pro1 / pro2 / pro3")
    await state.set_state(SetLevelState.waiting_for_level)

@router.message(SetLevelState.waiting_for_level)
async def process_level(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_LIST:
        return
    level = message.text.strip().lower()
    if level not in ["easy", "normal", "hard", "pro1", "pro2", "pro3"]:
        await message.answer("Ошибка: уровень должен быть easy, normal, hard, pro1, pro2 или pro3.")
        return
    data = await state.get_data()
    user_id = data["target_user_id"]
    await db.update_user(user_id, level=level)
    if level.startswith("pro"):
        await db.update_user(user_id, gym_level=level, gym_workouts_count=0)
    logger.info(f"Админ {message.from_user.id} установил уровень {level} для {user_id}")
    await message.answer(f"Уровень пользователя {user_id} изменён на {level}")
    await state.clear()
    await admin_panel(message)

# накрутка страйка
@router.callback_query(F.data == "admin_boost")
async def admin_boost_start(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_LIST:
        return
    await callback.message.delete()
    await callback.message.answer(
        "Введи ID пользователя или нажми кнопку 'Себе':",
        reply_markup=get_id_selection_keyboard("boost")
    )
    await state.set_state(BoostState.waiting_for_user_id)
    await callback.answer()

@router.callback_query(F.data == "admin_boost_self")
async def admin_boost_self(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_LIST:
        return
    user_id = callback.from_user.id
    if not await db.get_user(user_id):
        await callback.message.edit_text("Сначала зарегистрируйся через /start")
        await callback.answer()
        return
    await state.update_data(target_user_id=user_id)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="+5", callback_data="boost_5"),
         InlineKeyboardButton(text="+10", callback_data="boost_10")],
        [InlineKeyboardButton(text="+20", callback_data="boost_20"),
         InlineKeyboardButton(text="+100", callback_data="boost_100")],
        [InlineKeyboardButton(text="Отмена", callback_data="boost_cancel")]
    ])
    await callback.message.edit_text("Выбери, сколько добавить к страйку:", reply_markup=keyboard)
    await state.set_state(BoostState.waiting_for_value)
    await callback.answer()

@router.message(BoostState.waiting_for_user_id)
async def process_boost_user_id(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_LIST:
        return
    try:
        user_id = int(message.text.strip())
    except ValueError:
        await message.answer("Ошибка: ID должен быть числом.")
        return
    if not await db.get_user(user_id):
        await message.answer("Ошибка: пользователь не найден.")
        return
    await state.update_data(target_user_id=user_id)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="+5", callback_data="boost_5"),
         InlineKeyboardButton(text="+10", callback_data="boost_10")],
        [InlineKeyboardButton(text="+20", callback_data="boost_20"),
         InlineKeyboardButton(text="+100", callback_data="boost_100")],
        [InlineKeyboardButton(text="Отмена", callback_data="boost_cancel")]
    ])
    await message.answer("Выбери, сколько добавить к страйку:", reply_markup=keyboard)
    await state.set_state(BoostState.waiting_for_value)

@router.callback_query(BoostState.waiting_for_value, F.data.startswith("boost_"))
async def process_boost_value(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_LIST:
        return
    value = int(callback.data.split("_")[1])
    data = await state.get_data()
    user_id = data["target_user_id"]
    user = await db.get_user(user_id)
    if user:
        new_streak = user.get("streak", 0) + value
        new_total = user.get("total_workouts", 0) + value
        await db.update_user(user_id, streak=new_streak, total_workouts=new_total)
        logger.info(f"Админ {callback.from_user.id} накрутил {value} страйка пользователю {user_id}")
        await callback.message.edit_text(f"✅ Добавлено {value} к страйку пользователя {user_id}. Текущий страйк: {new_streak}")
    else:
        await callback.message.edit_text("Ошибка: пользователь не найден")
    await state.clear()
    await callback.answer()

@router.callback_query(BoostState.waiting_for_value, F.data == "boost_cancel")
async def boost_cancel(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_LIST:
        return
    await callback.message.edit_text("Операция отменена.")
    await state.clear()
    await callback.answer()

# статистика 
@router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_LIST:
        return
    users = await db.get_all_users()
    total = len(users)
    active_today = sum(1 for u in users if u.get("last_workout_date") == date.today().isoformat())
    avg_streak = sum(u.get("streak", 0) for u in users) / total if total else 0
    text = f"Всего пользователей: {total}\nАктивных сегодня: {active_today}\nСредний страйк: {avg_streak:.1f}"
    await callback.message.delete()
    await callback.message.answer(text, reply_markup=back_button())
    await callback.answer()

# удалить пользователя
@router.callback_query(F.data == "admin_delete_user")
async def admin_delete_user_start(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        return
    await callback.message.delete()
    await callback.message.answer("Введите ID пользователя для удаления:")
    await state.set_state(DeleteUserState.waiting_for_user_id)
    await callback.answer()

@router.message(DeleteUserState.waiting_for_user_id)
async def admin_delete_user_process(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        return
    try:
        user_id = int(message.text.strip())
    except ValueError:
        await message.answer("Ошибка: ID должен быть числом.")
        return
    user = await db.get_user(user_id)
    if not user:
        await message.answer("Пользователь не найден.")
        await state.clear()
        await admin_panel(message)
        return
    confirm_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Да, удалить", callback_data=f"confirm_delete_{user_id}")],
        [InlineKeyboardButton(text="❌ Нет, отмена", callback_data="admin_back")]
    ])
    await message.answer(f"Удалить пользователя {user_id} ({user.get('first_name') or user.get('username')})?",
                         reply_markup=confirm_keyboard)
    await state.clear()

@router.callback_query(F.data.startswith("confirm_delete_"))
async def admin_confirm_delete(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        return
    user_id = int(callback.data.split("_")[2])
    await db.delete_user(user_id)
    logger.info(f"Админ {callback.from_user.id} удалил пользователя {user_id}")
    await callback.message.edit_text(f"✅ Пользователь {user_id} удалён.")
    await callback.answer()
    await admin_panel(callback.message)

# логи и прочее
@router.callback_query(F.data == "admin_logs")
async def admin_logs(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_LIST:
        return
    if not os.path.exists(LOG_PATH):
        await callback.message.edit_text("Лог-файл не найден.", reply_markup=back_button())
    else:
        try:
            document = FSInputFile(LOG_PATH)
            await callback.message.answer_document(document, caption="bot.log")
            await callback.message.delete()
        except Exception as e:
            await callback.message.edit_text(f"Ошибка при отправке лога: {e}", reply_markup=back_button())
    await callback.answer()

@router.callback_query(F.data == "admin_test_remind")
async def admin_test_remind(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_LIST:
        return
    from utils.scheduler import workout_remind_print
    try:
        await workout_remind_print(callback.bot)
        await callback.message.edit_text("Напоминалка запущена. Проверь консоль/логи.", reply_markup=back_button())
    except Exception as e:
        await callback.message.edit_text(f"Ошибка: {e}", reply_markup=back_button())
    await callback.answer()

@router.callback_query(F.data == "admin_clear_logs")
async def admin_clear_logs(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_LIST:
        return
    try:
        open(LOG_PATH, "w").close()
        await callback.message.edit_text("Лог-файл очищен.", reply_markup=back_button())
    except Exception as e:
        await callback.message.edit_text(f"Ошибка: {e}", reply_markup=back_button())
    await callback.answer()

# рассылка 
@router.callback_query(F.data == "admin_broadcast")
async def admin_broadcast_start(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        return
    await callback.message.delete()
    await callback.message.answer("Введите текст сообщения для рассылки:\n(Отмена: /cancel)\nОБЯЗАТЕЛЬНО СОГЛАСОВАТЬ С @NikOneTG !!!")
    await state.set_state(BroadcastState.waiting_for_message)
    await callback.answer()

@router.message(BroadcastState.waiting_for_message)
async def broadcast_send(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_LIST:
        return
    if message.text == "/cancel":
        await state.clear()
        await message.answer("Рассылка отменена.")
        await admin_panel(message)
        return

    text = message.text
    users = await db.get_all_users()
    success = 0
    fail = 0
    await message.answer("Начинаю рассылку...")
    for user in users:
        try:
            await message.bot.send_message(user["user_id"], text)
            success += 1
            await asyncio.sleep(0.05)
        except Exception:
            fail += 1
    await state.clear()
    await message.answer(
        f"Рассылка завершена.\n"
        f"Отправлено: {success}\n"
        f"Не доставлено: {fail}"
    )
    await admin_panel(message)

# назад и закрыть
@router.callback_query(F.data == "admin_back")
async def admin_back(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_LIST:
        return
    try:
        await callback.message.delete()
    except TelegramBadRequest as e:
        if "message to delete not found" in str(e):
            pass
        else:
            raise e
    await callback.message.answer("Админ-панель", reply_markup=admin_keyboard())
    await callback.answer()

@router.callback_query(F.data == "admin_close")
async def admin_close(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_LIST:
        return
    await callback.message.delete()
    await callback.answer()