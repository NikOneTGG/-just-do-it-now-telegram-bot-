from aiogram import Router, F
from aiogram.types import CallbackQuery
from db_instance import db

router = Router()

# лидерборд
@router.callback_query(F.data == "leaderboard")
async def leaderboard_handler(callback: CallbackQuery):
    users = await db.get_all_users()
# фильтр страйка >0
    active_users = [u for u in users if u.get("streak", 0) > 0]

    if not active_users:
        user = await db.get_user(callback.from_user.id)
        if user and user.get("gender") == "female":
            await callback.message.answer("Пока никого нет, будь первой!")
        else:
            await callback.message.answer("Пока никого нет, будь первым!")
        await callback.answer()
        return

# сортировка по убыванию, 10 пользователей
    sorted_users = sorted(active_users, key=lambda x: x.get("streak", 0), reverse=True)[:10]

    response = "🏆 ЛИДЕРБОРД 🏆\n\n"
    for i, u in enumerate(sorted_users, 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        name = u.get("first_name") or u.get("username") or "Аноним"
        response += f"{medal} {name} — {u.get('streak', 0)} дней 🔥\n"

    await callback.message.delete()
    await callback.message.answer(response)
    await callback.answer()