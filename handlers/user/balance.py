from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

import database as db

router = Router()


@router.message(F.text == "👤 Hisobim")
async def my_balance(message: Message, state: FSMContext):
    await state.clear()
    await db.update_last_active(message.from_user.id)

    user = await db.get_user(message.from_user.id)
    if not user:
        await message.answer("❌ Foydalanuvchi topilmadi. /start ni bosing.")
        return

    orders_count = await db.count_user_orders(message.from_user.id)
    referrals_count = await db.count_referrals(message.from_user.id)

    await message.answer(
        f"👤 <b>Mening hisobim</b>\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 <b>Balans:</b>        {user['balance']:,} so'm\n"
        f"📦 <b>Buyurtmalar:</b>   {orders_count} ta\n"
        f"👥 <b>Referallar:</b>    {referrals_count} kishi\n"
        f"💳 <b>Kiritilgan pul:</b> {user['total_deposited']:,} so'm\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🆔 <b>ID:</b> <code>{message.from_user.id}</code>\n"
        f"📅 <b>Ro'yxatdan:</b> {user['joined_at'][:10]}",
        parse_mode="HTML"
    )
