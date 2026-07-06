from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import database as db
from keyboards import help_kb, cancel_kb, main_menu_kb
from config import ADMIN_ID

router = Router()

FAQ_TEXT = """
❓ <b>Ko'p beriladigan savollar (FAQ)</b>

━━━━━━━━━━━━━━━━━━━━━━━━━

<b>1. Buyurtma qancha vaqtda bajariladi?</b>
⏱ Odatda 5 daqiqadan 24 soatgacha.

<b>2. Pul qaytarib beriladi mi?</b>
💰 Agar buyurtma bajarilmagan bo'lsa, to'liq qaytariladi.

<b>3. Minimal to'ldirish summasi qancha?</b>
💳 Minimal: 1 000 so'm.

<b>4. Referral tizimi qanday ishlaydi?</b>
👥 Har bir taklif uchun 1 000 so'm balansingizga qo'shiladi.

<b>5. Xizmat sifati kafolatlanadimi?</b>
✅ Ha, barcha xizmatlar sifat kafolati bilan beriladi.

<b>6. Buyurtma bekor bo'lsa nima qilaman?</b>
📩 Yordam bo'limidan adminga murojat qiling.

<b>7. Qaysi tarmoqlar uchun xizmat bor?</b>
📱 Telegram, Instagram, YouTube, TikTok va boshqalar.

━━━━━━━━━━━━━━━━━━━━━━━━━
"""


class HelpStates(StatesGroup):
    waiting_message = State()


@router.message(F.text == "💬 Yordam")
async def help_main(message: Message, state: FSMContext):
    await state.clear()
    await db.update_last_active(message.from_user.id)
    await message.answer(
        "💬 <b>Yordam</b>\n\n"
        "Quyidagilardan birini tanlang:",
        parse_mode="HTML",
        reply_markup=help_kb()
    )


@router.callback_query(F.data == "help_admin_chat")
async def help_admin_chat(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "💬 <b>Admin bilan chat</b>\n\n"
        "Savolingiz yoki muammongizni yozing.\n"
        "Admin iloji boricha tez javob beradi! 📩",
        parse_mode="HTML"
    )
    await callback.message.answer(
        "✍️ Xabaringizni yozing:", reply_markup=cancel_kb()
    )
    await state.set_state(HelpStates.waiting_message)
    await callback.answer()


@router.callback_query(F.data == "help_faq")
async def help_faq(callback: CallbackQuery):
    await callback.message.edit_text(
        FAQ_TEXT,
        parse_mode="HTML",
        reply_markup=__import__("keyboards").back_kb("back_help")
    )
    await callback.answer()


@router.callback_query(F.data == "back_help")
async def back_help(callback: CallbackQuery):
    await callback.message.edit_text(
        "💬 <b>Yordam</b>\n\nQuyidagilardan birini tanlang:",
        parse_mode="HTML",
        reply_markup=help_kb()
    )
    await callback.answer()


@router.message(HelpStates.waiting_message, F.text == "❌ Bekor qilish")
async def cancel_help(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Bekor qilindi.", reply_markup=main_menu_kb())


@router.message(HelpStates.waiting_message)
async def send_help_message(message: Message, state: FSMContext):
    text = message.text or message.caption or "(media)"

    await db.save_message(
        user_id=message.from_user.id,
        full_name=message.from_user.full_name,
        text=text
    )

    # Adminga jo'natish
    try:
        await message.bot.send_message(
            ADMIN_ID,
            f"📩 <b>Yangi murojat!</b>\n\n"
            f"👤 <a href='tg://user?id={message.from_user.id}'>"
            f"{message.from_user.full_name}</a>\n"
            f"🆔 ID: <code>{message.from_user.id}</code>\n"
            f"━━━━━━━━━━━━━━━\n"
            f"📝 {text}\n"
            f"━━━━━━━━━━━━━━━\n"
            f"💬 Javob berish: /reply_{message.from_user.id}",
            parse_mode="HTML"
        )
    except Exception:
        pass

    await state.clear()
    await message.answer(
        "✅ <b>Xabaringiz adminga yuborildi!</b>\n\n"
        "⏳ Admin tez orada javob beradi.",
        parse_mode="HTML",
        reply_markup=main_menu_kb()
    )
