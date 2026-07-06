from aiogram import Router, F
from aiogram.types import Message

import database as db

router = Router()

GUIDE_TEXT = """
📖 <b>Bot Qo'llanmasi</b>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>🚀 Boshlash</b>
/start — Botni ishga tushirish va asosiy menyuni ochish.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>📦 Buyurtma berish</b>
1. "📦 Buyurtma berish" tugmasini bosing
2. Xizmat turini tanlang:
   • 🚀 Nakrutka → Platformani tanlang → Xizmatni tanlang
   • ⭐ Stars/Premium → Xizmatni tanlang
   • 🎁 Gift → Xizmatni tanlang
3. Miqdorni kiriting (raqam bilan)
4. Havolani kiriting (link)
5. Buyurtmani tasdiqlang

⚠️ <i>Buyurtma uchun balansingizda yetarli pul bo'lishi kerak!</i>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>📱 Raqam olish</b>
1. "📱 Raqam olish" tugmasini bosing
2. Server tanlang (Barqaror / Tezkor / Tejamkor)
3. Xizmatni tanlang va to'lang

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>💳 Hisob to'ldirish</b>
1. "💳 Hisob to'ldirish" tugmasini bosing
2. To'lov usulini tanlang (Click, Payme va boshqalar)
3. Ko'rsatilgan karta raqamiga pul o'tkazing
4. Summani kiriting
5. To'lov chekini (screenshot) yuboring
6. Admin tasdiqlaydi → balans to'ldiriladi

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>💰 Pul ishlash (Referral)</b>
1. "💰 Pul ishlash" tugmasini bosing
2. Shaxsiy havolangizni oling
3. Do'stlaringizga yuboring
4. Har bir ro'yxatdan o'tgan do'st uchun
   💵 <b>1 000 so'm</b> balansingizga qo'shiladi!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>📋 Buyurtmalarim</b>
So'nggi 20 ta buyurtmangiz va ularning holati ko'rsatiladi:
⏳ Kutilmoqda | 🔄 Jarayonda | ✅ Bajarildi | ❌ Bekor

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>💬 Yordam</b>
• Admin bilan bevosita chat qiling
• FAQ (Ko'p beriladigan savollar) bo'limini o'qing

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>👤 Hisobim</b>
Balansingiz, buyurtmalar soni, referallar soni
va kiritilgan pullar miqdori ko'rsatiladi.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""


@router.message(F.text == "📖 Qo'llanma")
async def guide(message: Message):
    await db.update_last_active(message.from_user.id)
    await message.answer(GUIDE_TEXT, parse_mode="HTML")
