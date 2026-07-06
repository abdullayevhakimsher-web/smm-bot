from aiogram import Router, F
from aiogram.types import CallbackQuery

import database as db
from keyboards import admin_main_kb
from config import ADMIN_ID

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


@router.callback_query(F.data == "adm:stats")
async def admin_stats(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return

    stats = await db.get_stats()

    text = (
        f"📊 <b>Bot Statistikasi</b>\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 <b>Jami foydalanuvchilar:</b> {stats['total_users']:,}\n"
        f"🟢 <b>Bugun faol:</b> {stats['active_today']:,}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📦 <b>Jami buyurtmalar:</b> {stats['total_orders']:,}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 <b>Jami kiritilgan:</b> {stats['total_deposited']:,} so'm\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📩 <b>O'qilmagan murojatlar:</b> {stats['unread_msgs']}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━"
    )

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔙 Orqaga", callback_data="adm:back"))

    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=builder.as_markup())
    await callback.answer()
