from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

import database as db
from keyboards import cancel_kb, admin_main_kb
from config import ADMIN_ID

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


class ChannelStates(StatesGroup):
    waiting_add = State()
    waiting_del = State()


# ── Kanal qo'shish ───────────────────────────────────────────────────
@router.callback_query(F.data == "adm:add_channel")
async def admin_add_channel(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return

    await callback.message.edit_text(
        "📢 <b>Majburiy kanal qo'shish</b>\n\n"
        "Kanal username yoki ID sini kiriting.\n\n"
        "📋 <b>Misol:</b>\n"
        "• <code>@kanalname</code>\n"
        "• <code>-1001234567890</code>\n\n"
        "⚠️ Bot kanalda admin bo'lishi kerak!",
        parse_mode="HTML"
    )
    await callback.message.answer(
        "✍️ Kanal ma'lumotini kiriting:", reply_markup=cancel_kb()
    )
    await state.set_state(ChannelStates.waiting_add)
    await callback.answer()


@router.message(ChannelStates.waiting_add, F.text == "❌ Bekor qilish")
async def cancel_add_channel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Bekor qilindi.")


@router.message(ChannelStates.waiting_add)
async def save_channel(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    channel_input = message.text.strip()

    # Kanal ma'lumotini olish
    try:
        chat = await message.bot.get_chat(channel_input)
        channel_id = str(chat.id)
        channel_name = chat.title or channel_input
    except Exception:
        await message.answer(
            f"❌ Kanal topilmadi: <code>{channel_input}</code>\n"
            f"Bot kanalda admin ekanligini tekshiring.",
            parse_mode="HTML"
        )
        return

    added = await db.add_channel(channel_id, channel_name)
    if added:
        await message.answer(
            f"✅ <b>Kanal qo'shildi!</b>\n\n"
            f"📢 {channel_name}\n"
            f"🆔 <code>{channel_id}</code>",
            parse_mode="HTML"
        )
    else:
        await message.answer("⚠️ Bu kanal allaqachon qo'shilgan!")

    await state.clear()


# ── Kanalni o'chirish ─────────────────────────────────────────────────
@router.callback_query(F.data == "adm:del_channel")
async def admin_del_channel(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return

    channels = await db.get_channels()

    if not channels:
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="🔙 Orqaga", callback_data="adm:back"))
        await callback.message.edit_text(
            "🔕 <b>Kanallar ro'yxati bo'sh!</b>",
            parse_mode="HTML",
            reply_markup=builder.as_markup()
        )
        await callback.answer()
        return

    builder = InlineKeyboardBuilder()
    for ch in channels:
        name = ch["channel_name"] or ch["channel_id"]
        builder.row(InlineKeyboardButton(
            text=f"🗑 {name}",
            callback_data=f"delch:{ch['channel_id']}"
        ))
    builder.row(InlineKeyboardButton(text="🔙 Orqaga", callback_data="adm:back"))

    await callback.message.edit_text(
        "🔕 <b>O'chirish uchun kanalni tanlang:</b>",
        parse_mode="HTML",
        reply_markup=builder.as_markup()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("delch:"))
async def delete_channel(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return

    channel_id = callback.data.split(":", 1)[1]
    await db.remove_channel(channel_id)

    await callback.answer(f"✅ Kanal o'chirildi!", show_alert=True)

    # Yangilangan ro'yxat
    channels = await db.get_channels()
    if not channels:
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="🔙 Orqaga", callback_data="adm:back"))
        await callback.message.edit_text(
            "🔕 <b>Kanallar ro'yxati bo'sh!</b>",
            parse_mode="HTML",
            reply_markup=builder.as_markup()
        )
        return

    builder = InlineKeyboardBuilder()
    for ch in channels:
        name = ch["channel_name"] or ch["channel_id"]
        builder.row(InlineKeyboardButton(
            text=f"🗑 {name}",
            callback_data=f"delch:{ch['channel_id']}"
        ))
    builder.row(InlineKeyboardButton(text="🔙 Orqaga", callback_data="adm:back"))
    await callback.message.edit_reply_markup(reply_markup=builder.as_markup())
