from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

import database as db
from keyboards import main_menu_kb, back_kb
from config import ADMIN_ID

router = Router()

BOT_INFO_TEXT = """
╔══════════════════════════════╗
       🌟 SMM BOT XUSH KELIBSIZ! 🌟
╚══════════════════════════════╝

🚀 <b>SMM Bot</b> — ijtimoiy tarmoqlar uchun 
   professional xizmatlar platformasi!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📦 <b>Bizning xizmatlar:</b>
   • 🚀 Nakrutka (Telegram, Instagram, YouTube, TikTok)
   • ⭐ Telegram Stars va Premium
   • 🎁 Telegram Gift
   • 📱 Virtual raqamlar (3 ta server)
   • 🆓 Tekin xizmatlar

💡 <b>Afzalliklar:</b>
   ✅ Tez bajariladi
   ✅ Sifatli xizmat
   ✅ Qulay narxlar
   ✅ 24/7 ishlaymiz
   ✅ Referral tizimi (1 000 so'm/taklif)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👇 Quyidagi tugmalardan foydalaning:
"""


async def check_subscription(bot, user_id: int) -> list:
    """Majburiy kanallarga obuna tekshirish"""
    channels = await db.get_channels()
    not_subscribed = []
    for ch in channels:
        try:
            member = await bot.get_chat_member(ch["channel_id"], user_id)
            if member.status in ("left", "kicked", "banned"):
                not_subscribed.append(ch)
        except Exception:
            pass
    return not_subscribed


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()

    # Referral parametrini olish
    args = message.text.split()
    referrer_id = None
    if len(args) > 1:
        try:
            ref_id = int(args[1].replace("ref_", ""))
            if ref_id != message.from_user.id:
                referrer_id = ref_id
        except Exception:
            pass

    # Foydalanuvchini ro'yxatdan o'tkazish
    is_new = await db.register_user(
        user_id=message.from_user.id,
        username=message.from_user.username or "",
        full_name=message.from_user.full_name or "",
        referrer_id=referrer_id
    )
    await db.update_last_active(message.from_user.id)

    # Majburiy kanal tekshirish
    not_subscribed = await check_subscription(message.bot, message.from_user.id)
    if not_subscribed:
        links = "\n".join(
            [f"➡️ <a href='https://t.me/{ch['channel_id'].lstrip('@')}'>{ch['channel_name'] or ch['channel_id']}</a>"
             for ch in not_subscribed]
        )
        await message.answer(
            f"⚠️ <b>Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling:</b>\n\n"
            f"{links}\n\n"
            f"✅ Obuna bo'lgach, /start ni bosing.",
            parse_mode="HTML",
            disable_web_page_preview=True
        )
        return

    # Admin referral bonus xabari
    if is_new and referrer_id:
        try:
            await message.bot.send_message(
                referrer_id,
                f"🎉 <b>Tabriklaymiz!</b>\n"
                f"Sizning havolangiz orqali yangi foydalanuvchi qo'shildi!\n"
                f"💰 <b>+1 000 so'm</b> balansingizga qo'shildi!",
                parse_mode="HTML"
            )
        except Exception:
            pass

    await message.answer(
        BOT_INFO_TEXT,
        parse_mode="HTML",
        reply_markup=main_menu_kb()
    )


@router.callback_query(F.data == "back_main")
async def back_to_main(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        BOT_INFO_TEXT,
        parse_mode="HTML",
    )
    await callback.answer()
