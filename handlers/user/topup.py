from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import database as db
from keyboards import topup_methods_kb, cancel_kb, main_menu_kb
from config import PAYMENT_CARDS, ADMIN_ID

router = Router()


class TopupStates(StatesGroup):
    waiting_amount = State()
    waiting_receipt = State()


PAYMENT_LABELS = {
    "click":   "💳 Click",
    "payme":   "💳 Payme",
    "xazna":   "💳 Xazna",
    "zoomrad": "💳 Zoomrad",
    "paynet":  "💳 Paynet",
    "beepul":  "💳 Beepul",
    "oson":    "💳 Oson",
    "uzcard":  "🏧 UzCard",
    "alif":    "💳 Alif",
    "humo":    "🏧 Humo",
    "bank":    "🏦 Bank karta",
}


@router.message(F.text == "💳 Hisob to'ldirish")
async def topup_main(message: Message, state: FSMContext):
    await state.clear()
    await db.update_last_active(message.from_user.id)
    await message.answer(
        "💳 <b>Hisob to'ldirish</b>\n\n"
        "To'lov usulini tanlang:",
        parse_mode="HTML",
        reply_markup=topup_methods_kb()
    )


@router.callback_query(F.data.startswith("topup:"))
async def topup_method_selected(callback: CallbackQuery, state: FSMContext):
    method = callback.data.split(":")[1]

    if method == "admin":
        await callback.message.edit_text(
            "📩 <b>Adminga murojat</b>\n\n"
            "Hisob to'ldirish uchun admin bilan bog'laning.\n"
            "To'lov summasini va foydalanuvchi ID ingizni yuboring.",
            parse_mode="HTML"
        )
        await callback.answer()
        return

    card = PAYMENT_CARDS.get(method, "Noma'lum")
    label = PAYMENT_LABELS.get(method, method.upper())

    await state.update_data(method=method)
    await callback.message.edit_text(
        f"💳 <b>{label} orqali to'ldirish</b>\n\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"🏦 <b>Karta raqami:</b>\n"
        f"<code>{card}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━\n\n"
        f"📋 <b>Ko'rsatma:</b>\n"
        f"1. Yuqoridagi karta raqamiga pul o'tkazing\n"
        f"2. O'tkazma summasini kiriting\n"
        f"3. Chek (screenshot) yuboring\n\n"
        f"💰 To'lash summangizni kiriting (so'mda):",
        parse_mode="HTML"
    )
    await callback.message.answer(
        "❌ Bekor qilish uchun:", reply_markup=cancel_kb()
    )
    await state.set_state(TopupStates.waiting_amount)
    await callback.answer()


@router.message(TopupStates.waiting_amount, F.text == "❌ Bekor qilish")
async def cancel_topup_amount(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Bekor qilindi.", reply_markup=main_menu_kb())


@router.message(TopupStates.waiting_amount)
async def topup_amount(message: Message, state: FSMContext):
    text = message.text.replace(" ", "").replace(",", "")
    if not text.isdigit():
        await message.answer("⚠️ Iltimos, faqat raqam kiriting (so'mda)!")
        return

    amount = int(text)
    if amount < 1000:
        await message.answer("⚠️ Minimal to'ldirish miqdori: 1 000 so'm")
        return

    await state.update_data(amount=amount)
    await message.answer(
        f"✅ Summa: <b>{amount:,} so'm</b>\n\n"
        f"📸 Endi to'lov chekini (screenshot) yuboring:",
        parse_mode="HTML"
    )
    await state.set_state(TopupStates.waiting_receipt)


@router.message(TopupStates.waiting_receipt, F.text == "❌ Bekor qilish")
async def cancel_topup_receipt(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Bekor qilindi.", reply_markup=main_menu_kb())


@router.message(TopupStates.waiting_receipt, F.photo | F.document | F.text)
async def topup_receipt(message: Message, state: FSMContext):
    data = await state.get_data()
    method = data.get("method", "noma'lum")
    amount = data.get("amount", 0)
    label = PAYMENT_LABELS.get(method, method)

    await db.create_deposit(message.from_user.id, method, amount)

    # Adminga xabar
    try:
        caption = (
            f"💰 <b>Yangi to'ldirish so'rovi!</b>\n\n"
            f"👤 Foydalanuvchi: <a href='tg://user?id={message.from_user.id}'>"
            f"{message.from_user.full_name}</a>\n"
            f"🆔 ID: <code>{message.from_user.id}</code>\n"
            f"💳 Usul: {label}\n"
            f"💰 Summa: <b>{amount:,} so'm</b>\n\n"
            f"✅ Tasdiqlash uchun: /topup_confirm_{message.from_user.id}_{amount}"
        )
        if message.photo:
            await message.bot.send_photo(
                ADMIN_ID,
                message.photo[-1].file_id,
                caption=caption,
                parse_mode="HTML"
            )
        elif message.document:
            await message.bot.send_document(
                ADMIN_ID,
                message.document.file_id,
                caption=caption,
                parse_mode="HTML"
            )
        else:
            await message.bot.send_message(
                ADMIN_ID,
                caption + f"\n\n📝 Izoh: {message.text}",
                parse_mode="HTML"
            )
    except Exception:
        pass

    await state.clear()
    await message.answer(
        f"✅ <b>So'rovingiz qabul qilindi!</b>\n\n"
        f"💰 Summa: {amount:,} so'm\n"
        f"💳 Usul: {label}\n\n"
        f"⏳ Admin tekshirgandan so'ng balansingiz to'ldiriladi.\n"
        f"Odatda 5-30 daqiqa ichida.",
        parse_mode="HTML",
        reply_markup=main_menu_kb()
    )
