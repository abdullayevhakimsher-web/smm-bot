from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

import database as db
from keyboards import number_servers_kb, number_services_kb

router = Router()


@router.message(F.text == "📱 Raqam olish")
async def number_main(message: Message, state: FSMContext):
    await state.clear()
    await db.update_last_active(message.from_user.id)
    await message.answer(
        "📱 <b>Raqam olish</b>\n\n"
        "Virtual raqam olish uchun server tanlang:\n\n"
        "🟢 <b>Server 1 — Barqaror</b>: Ishonchli, barqaror ulanish\n"
        "⚡ <b>Server 2 — Tezkor</b>: Eng tez xizmat ko'rsatish\n"
        "💚 <b>Server 3 — Tejamkor</b>: Qulay narxlar",
        parse_mode="HTML",
        reply_markup=number_servers_kb()
    )


@router.callback_query(F.data.startswith("numserver:"))
async def server_selected(callback: CallbackQuery, state: FSMContext):
    server = callback.data.split(":")[1]
    await state.update_data(server=server)

    server_names = {
        "server1": "🟢 Server 1 — Barqaror",
        "server2": "⚡ Server 2 — Tezkor",
        "server3": "💚 Server 3 — Tejamkor",
    }
    label = server_names.get(server, server)

    services = await db.get_number_services(server)
    await callback.message.edit_text(
        f"📱 <b>Raqam olish → {label}</b>\n\n"
        f"Mavjud xizmatlar:",
        parse_mode="HTML",
        reply_markup=number_services_kb(services, server)
    )
    await callback.answer()


@router.callback_query(F.data == "back_num_servers")
async def back_num_servers(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "📱 <b>Raqam olish</b>\n\nServer tanlang:",
        parse_mode="HTML",
        reply_markup=number_servers_kb()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("numsvc:"))
async def number_service_selected(callback: CallbackQuery, state: FSMContext):
    svc_id = int(callback.data.split(":")[1])

    from database import DB_PATH
    import aiosqlite
    async with aiosqlite.connect(DB_PATH) as dbc:
        dbc.row_factory = aiosqlite.Row
        async with dbc.execute(
            "SELECT * FROM number_services WHERE id = ?", (svc_id,)
        ) as cur:
            svc = await cur.fetchone()

    if not svc:
        await callback.answer("❌ Xizmat topilmadi!", show_alert=True)
        return

    balance = await db.get_user_balance(callback.from_user.id)
    if balance < svc["price"]:
        await callback.answer(
            f"❌ Balansingiz yetarli emas!\n"
            f"Kerak: {svc['price']:,} so'm\n"
            f"Balans: {balance:,} so'm",
            show_alert=True
        )
        return

    await callback.message.edit_text(
        f"📱 <b>{svc['name']}</b>\n\n"
        f"📝 {svc['description'] or ''}\n\n"
        f"💰 Narx: {svc['price']:,} so'm\n"
        f"💳 Balans: {balance:,} so'm\n\n"
        f"⏳ Raqam tayyor bo'lishi uchun biroz kuting...\n"
        f"(Bu funksiya tez orada to'liq ishga tushadi)",
        parse_mode="HTML"
    )
    await callback.answer("✅ So'rov qabul qilindi!")
