from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

import database as db
from config import ADMIN_ID

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


@router.callback_query(F.data == "adm:users")
async def admin_users(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return

    users = await db.get_active_users()

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔙 Orqaga", callback_data="adm:back"))

    if not users:
        await callback.message.edit_text(
            "👥 <b>Faol foydalanuvchilar</b>\n\n"
            "❌ Oxirgi 24 soatda faol foydalanuvchi yo'q.",
            parse_mode="HTML",
            reply_markup=builder.as_markup()
        )
        await callback.answer()
        return

    text = f"👥 <b>Faol foydalanuvchilar (24 soat): {len(users)} ta</b>\n\n"
    for i, user in enumerate(users[:30], 1):
        username = f"@{user['username']}" if user["username"] else "—"
        text += (
            f"{i}. <a href='tg://user?id={user['user_id']}'>{user['full_name']}</a> "
            f"{username}\n"
            f"   🕐 {user['last_active'][:16]}\n"
        )

    if len(users) > 30:
        text += f"\n... va yana {len(users) - 30} ta"

    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=builder.as_markup()
    )
    await callback.answer()
