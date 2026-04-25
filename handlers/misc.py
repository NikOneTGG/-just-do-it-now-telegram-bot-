from aiogram import Router
from aiogram.types import Message
from db_instance import db

router = Router()

@router.message(lambda message: message.text == "Лидерборд")
async def leaderboard_handler(message: Message) -> None:
    users = await db.get_all_users()
    if not users:
        user = await db.get_user(message.from_user.id)
        if user and user.get("gender") == "female":
            await message.answer("Пока никого нет, будь первой!")
        else:
            await message.answer("Пока никого нет, будь первым!")
        return

    sorted_users = sorted(users, key=lambda x: x.get("streak", 0), reverse=True)[:10]
    response = "🏆 ЛИДЕРБОРД 🏆\n\n"
    for i, u in enumerate(sorted_users, 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        name = u.get("first_name") or u.get("username") or "Аноним"
        response += f"{medal} {name} — {u.get('streak', 0)} дней 🔥\n"
    await message.answer(response)