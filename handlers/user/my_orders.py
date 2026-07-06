from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

import database as db
from keyboards import main_menu_kb

router = Router()

STATUS_EMOJI = {
    "pending":    "⏳",
    "processing": "🔄",
    "completed":  "✅",
    "cancelled":  "❌",
    "partial":    "⚡",
}


@router.message(F.text == "📋 Buyurtmalarim")
async def my_orders(message: Message, state: FSMContext):
    await state.clear()
    await db.update_last_active(message.from_user.id)

    orders = await db.get_user_orders(message.from_user.id)

    if not orders:
        await message.answer(
            "📋 <b>Buyurtmalarim</b>\n\n"
            "❌ Sizda hali buyurtma yo'q.\n"
            "📦 Birinchi buyurtmangizni bering!",
            parse_mode="HTML"
        )
        return

    text = "📋 <b>Oxirgi 20 ta buyurtma:</b>\n\n"
    for i, order in enumerate(orders, 1):
        emoji = STATUS_EMOJI.get(order["status"], "❓")
        text += (
            f"{i}. {emoji} <b>{order['service_name'] or 'Noma\'lum'}</b>\n"
            f"   🔢 Miqdor: {order['quantity']:,} | 💰 {order['price']:,} so'm\n"
            f"   📅 {order['created_at'][:16]}\n\n"
        )

    await message.answer(text, parse_mode="HTML")
