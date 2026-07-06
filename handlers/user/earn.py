from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

import database as db

router = Router()


@router.message(F.text == "💰 Pul ishlash")
async def earn_money(message: Message, state: FSMContext):
    await state.clear()
    await db.update_last_active(message.from_user.id)

    referrals_count = await db.count_referrals(message.from_user.id)
    bot_username = (await message.bot.get_me()).username
    ref_link = f"https://t.me/{bot_username}?start=ref_{message.from_user.id}"

    earned = referrals_count * 1000

    await message.answer(
        f"💰 <b>Pul ishlash — Referral tizimi</b>\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🔗 <b>Sizning havola:</b>\n"
        f"<code>{ref_link}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👥 <b>Taklif qilganlar:</b> {referrals_count} kishi\n"
        f"💵 <b>Jami ishlagan:</b> {earned:,} so'm\n\n"
        f"🎁 <b>Mukofot:</b> Har bir taklif uchun\n"
        f"          <b>💰 1 000 so'm</b>\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📋 <b>Qanday ishlaydi?</b>\n"
        f"1️⃣ Havolani do'stlaringizga yuboring\n"
        f"2️⃣ Do'stingiz /start bossin\n"
        f"3️⃣ Balansingizga avtomatik 1 000 so'm qo'shiladi\n\n"
        f"🚀 Qancha ko'p taklif qilsangiz, shuncha ko'p ishlaysiz!",
        parse_mode="HTML"
    )
