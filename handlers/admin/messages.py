from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

import database as db
from config import ADMIN_ID

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


@router.callback_query(F.data == "adm:messages")
async def admin_messages(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return

    messages = await db.get_all_messages()

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔙 Orqaga", callback_data="adm:back"))

    if not messages:
        await callback.message.edit_text(
            "💬 <b>Murojatlar</b>\n\n❌ Hozircha murojatlar yo'q.",
            parse_mode="HTML",
            reply_markup=builder.as_markup()
        )
        await callback.answer()
        return

    text = "💬 <b>Oxirgi murojatlar (50 ta):</b>\n\n"
    for msg in messages:
        status = "🔴" if not msg["is_read"] else "✅"
        text += (
            f"{status} <b>{msg['full_name']}</b> "
            f"(<code>{msg['user_id']}</code>)\n"
            f"   📅 {msg['created_at'][:16]}\n"
            f"   📝 {msg['text'][:100]}{'...' if len(msg['text']) > 100 else ''}\n"
            f"   💬 /reply_{msg['user_id']}\n\n"
        )

    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=builder.as_markup()
    )
    await callback.answer()
