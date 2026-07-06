from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command

import database as db
from keyboards import admin_main_kb, cancel_kb
from config import ADMIN_ID, ADMIN_COMMAND

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


# ── Admin kirishi ─────────────────────────────────────────────────────
@router.message(Command(ADMIN_COMMAND))
async def admin_entry(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.answer("❌ Sizda bu buyruqni ishlatish huquqi yo'q!")
        return

    await state.clear()
    await message.answer(
        f"🔐 <b>Admin Panel</b>\n\n"
        f"👋 Xush kelibsiz, Admin!\n\n"
        f"Quyidagi bo'limlardan birini tanlang:",
        parse_mode="HTML",
        reply_markup=admin_main_kb()
    )


# ── Admin panel orqaga ─────────────────────────────────────────────────
@router.callback_query(F.data == "adm:back")
async def admin_back(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    await state.clear()
    await callback.message.edit_text(
        "🔐 <b>Admin Panel</b>\n\nBo'limni tanlang:",
        parse_mode="HTML",
        reply_markup=admin_main_kb()
    )
    await callback.answer()


# ── Foydalanuvchiga javob berish (/reply_USER_ID) ─────────────────────
@router.message(F.text.startswith("/reply_"))
async def admin_reply(message: Message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split("_", 1)
    if len(parts) < 2:
        await message.answer("⚠️ Format: /reply_USER_ID\nSo'ng javob matnini yozing.")
        return
    await message.answer(
        "✍️ Javob matnini yozing yoki faylni yuboring.\n"
        f"User ID: <code>{parts[1]}</code>",
        parse_mode="HTML"
    )


# ── Balans to'ldirish tasdiqlash (/topup_confirm_USERID_AMOUNT) ───────
@router.message(F.text.startswith("/topup_confirm_"))
async def topup_confirm(message: Message):
    if not is_admin(message.from_user.id):
        return
    try:
        parts = message.text.split("_")
        user_id = int(parts[2])
        amount = int(parts[3])
    except Exception:
        await message.answer("⚠️ Format xato. /topup_confirm_USERID_AMOUNT")
        return

    await db.add_balance(user_id, amount)

    try:
        await message.bot.send_message(
            user_id,
            f"✅ <b>Balansingiz to'ldirildi!</b>\n\n"
            f"💰 +{amount:,} so'm\n\n"
            f"Xarid qilishingiz mumkin! 🛒",
            parse_mode="HTML"
        )
    except Exception:
        pass

    await message.answer(
        f"✅ Foydalanuvchi <code>{user_id}</code> ga\n"
        f"<b>{amount:,} so'm</b> qo'shildi!",
        parse_mode="HTML"
    )
