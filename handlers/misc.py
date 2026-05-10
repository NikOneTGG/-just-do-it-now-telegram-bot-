from aiogram import Router, F
from aiogram.types import CallbackQuery
from db_instance import db
from inlinekey import leaderboard_menu

router = Router()

# склонения для лидерборда
def declension_days(n: int) -> str:
    if 10 <= n % 100 <= 20:
        return "дней"
    if n % 10 == 1:
        return "день"
    if 2 <= n % 10 <= 4:
        return "дня"
    return "дней"

# обработчик лидерборда
@router.callback_query(F.data == "leaderboard")
async def leaderboard_handler(callback: CallbackQuery):
    users = await db.get_all_users()
    active_users = [u for u in users if u.get("streak", 0) > 0]
    # проверка пользователей в лидерборде
    if not active_users:
        user = await db.get_user(callback.from_user.id)
        if user and user.get("gender") == "female":
            await callback.message.answer("Пока никого нет, будь первой!")
        else:
            await callback.message.answer("Пока никого нет, будь первым!")
        await callback.answer()
        return
# сортировка пользователей >0
    sorted_users = sorted(active_users, key=lambda x: x.get("streak", 0), reverse=True)[:10]
# визуал
    response = "ЛИДЕРБОРД\n\n"
    for i, u in enumerate(sorted_users, 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        name = u.get("first_name") or u.get("username") or "Аноним"
        response += f"{medal} {name} — {u.get('streak', 0)} {declension_days(u.get('streak', 0))} 🔥\n"
# выход в меню
    await callback.message.delete()
    await callback.message.answer(response, reply_markup=leaderboard_menu())
    await callback.answer()