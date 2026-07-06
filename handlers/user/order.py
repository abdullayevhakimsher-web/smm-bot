from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import database as db
from keyboards import (
    order_categories_kb, nakrutka_platforms_kb,
    services_list_kb, confirm_order_kb, cancel_kb, main_menu_kb
)
from config import ADMIN_ID

router = Router()


class OrderStates(StatesGroup):
    waiting_link = State()
    waiting_quantity = State()
    confirming = State()


# ── Buyurtma berish tugmasi ────────────────────────────────────────────
@router.message(F.text == "📦 Buyurtma berish")
async def order_main(message: Message, state: FSMContext):
    await state.clear()
    await db.update_last_active(message.from_user.id)
    await message.answer(
        "📦 <b>Buyurtma berish</b>\n\n"
        "Quyidagi xizmat turlaridan birini tanlang:",
        parse_mode="HTML",
        reply_markup=order_categories_kb()
    )


# ── Kategoriya tanlash ─────────────────────────────────────────────────
@router.callback_query(F.data.startswith("order_cat:"))
async def order_category(callback: CallbackQuery, state: FSMContext):
    cat = callback.data.split(":")[1]
    await state.update_data(category=cat)

    if cat == "nakrutka":
        await callback.message.edit_text(
            "🚀 <b>Nakrutka</b>\n\nPlatformani tanlang:",
            parse_mode="HTML",
            reply_markup=nakrutka_platforms_kb()
        )
    elif cat in ("stars", "gift"):
        label = "⭐ Telegram Stars / Premium" if cat == "stars" else "🎁 Telegram Gift"
        services = await db.get_services(cat)
        await callback.message.edit_text(
            f"{label}\n\nMavjud xizmatlar:",
            parse_mode="HTML",
            reply_markup=services_list_kb(services, back_cb="back_order_cat")
        )
    await callback.answer()


# ── Nakrutka platformasi ──────────────────────────────────────────────
@router.callback_query(F.data.startswith("nakrutka_sub:"))
async def nakrutka_sub(callback: CallbackQuery, state: FSMContext):
    sub = callback.data.split(":")[1]
    await state.update_data(subcategory=sub)

    platform_names = {
        "telegram": "📱 Telegram",
        "instagram": "📸 Instagram",
        "youtube": "▶️ YouTube",
        "tiktok": "🎵 TikTok",
        "tekin": "🆓 Tekin Xizmatlar",
    }
    label = platform_names.get(sub, sub)
    services = await db.get_services("nakrutka", sub)

    await callback.message.edit_text(
        f"🚀 Nakrutka → {label}\n\nMavjud xizmatlar:",
        parse_mode="HTML",
        reply_markup=services_list_kb(services, back_cb="back_nakrutka_platforms")
    )
    await callback.answer()


# ── Orqaga: kategoriyalar ─────────────────────────────────────────────
@router.callback_query(F.data == "back_order_cat")
async def back_order_cat(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "📦 <b>Buyurtma berish</b>\n\nQuyidagi xizmat turlaridan birini tanlang:",
        parse_mode="HTML",
        reply_markup=order_categories_kb()
    )
    await callback.answer()


@router.callback_query(F.data == "back_nakrutka_platforms")
async def back_nakrutka(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "🚀 <b>Nakrutka</b>\n\nPlatformani tanlang:",
        parse_mode="HTML",
        reply_markup=nakrutka_platforms_kb()
    )
    await callback.answer()


# ── Xizmat tanlash ────────────────────────────────────────────────────
@router.callback_query(F.data.startswith("svc:"))
async def service_selected(callback: CallbackQuery, state: FSMContext):
    svc_id = int(callback.data.split(":")[1])
    svc = await db.get_service_by_id(svc_id)
    if not svc:
        await callback.answer("❌ Xizmat topilmadi!", show_alert=True)
        return

    await state.update_data(
        service_id=svc_id,
        service_name=svc["name"],
        price=svc["price"],
        min_qty=svc["min_qty"],
        max_qty=svc["max_qty"],
    )

    await callback.message.edit_text(
        f"📋 <b>{svc['name']}</b>\n\n"
        f"📝 {svc['description'] or 'Tavsif yo\'q'}\n\n"
        f"💰 <b>Narx:</b> {svc['price']:,} so'm / birlik\n"
        f"📊 <b>Min/Max:</b> {svc['min_qty']} — {svc['max_qty']}\n\n"
        f"🔢 Miqdorni kiriting (raqam):",
        parse_mode="HTML"
    )
    await callback.message.answer(
        "❌ Bekor qilish uchun tugmani bosing:",
        reply_markup=cancel_kb()
    )
    await state.set_state(OrderStates.waiting_quantity)
    await callback.answer()


# ── Miqdor kiritish ──────────────────────────────────────────────────
@router.message(OrderStates.waiting_quantity, F.text == "❌ Bekor qilish")
async def cancel_order_qty(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Bekor qilindi.", reply_markup=main_menu_kb())


@router.message(OrderStates.waiting_quantity)
async def get_quantity(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("⚠️ Iltimos, faqat raqam kiriting!")
        return

    data = await state.get_data()
    qty = int(message.text)

    if qty < data["min_qty"] or qty > data["max_qty"]:
        await message.answer(
            f"⚠️ Miqdor {data['min_qty']} dan {data['max_qty']} gacha bo'lishi kerak!"
        )
        return

    await state.update_data(quantity=qty)
    await message.answer(
        "🔗 Havolani kiriting (link):\n"
        "Misol: <code>https://t.me/yourchannelname</code>",
        parse_mode="HTML"
    )
    await state.set_state(OrderStates.waiting_link)


# ── Havola kiritish ────────────────────────────────────────────────────
@router.message(OrderStates.waiting_link, F.text == "❌ Bekor qilish")
async def cancel_order_link(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Bekor qilindi.", reply_markup=main_menu_kb())


@router.message(OrderStates.waiting_link)
async def get_link(message: Message, state: FSMContext):
    data = await state.get_data()
    link = message.text.strip()
    await state.update_data(link=link)

    total = data["price"] * data["quantity"]
    balance = await db.get_user_balance(message.from_user.id)

    balance_status = "✅ Yetarli" if balance >= total else f"❌ Yetarli emas (balansingiz: {balance:,} so'm)"

    await message.answer(
        f"📋 <b>Buyurtmani tasdiqlash</b>\n\n"
        f"🛒 <b>Xizmat:</b> {data['service_name']}\n"
        f"🔢 <b>Miqdor:</b> {data['quantity']:,}\n"
        f"🔗 <b>Havola:</b> <code>{link}</code>\n"
        f"💰 <b>Jami narx:</b> {total:,} so'm\n"
        f"💳 <b>Balans:</b> {balance:,} so'm — {balance_status}",
        parse_mode="HTML",
        reply_markup=confirm_order_kb(data["service_id"])
    )
    await message.answer("Asosiy menyu:", reply_markup=main_menu_kb())
    await state.set_state(OrderStates.confirming)


# ── Buyurtmani tasdiqlash ──────────────────────────────────────────────
@router.callback_query(F.data.startswith("confirm_order:"))
async def confirm_order(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    total = data["price"] * data["quantity"]

    success = await db.deduct_balance(callback.from_user.id, total)
    if not success:
        await callback.answer(
            "❌ Balansingiz yetarli emas! Hisob to'ldiring.",
            show_alert=True
        )
        return

    await db.create_order(
        user_id=callback.from_user.id,
        category=data.get("category", ""),
        subcategory=data.get("subcategory", ""),
        service_id=data.get("service_id"),
        service_name=data.get("service_name"),
        quantity=data.get("quantity"),
        price=total,
        link=data.get("link", "")
    )

    # Adminga xabar
    try:
        await callback.bot.send_message(
            ADMIN_ID,
            f"🆕 <b>Yangi buyurtma!</b>\n\n"
            f"👤 Foydalanuvchi: <a href='tg://user?id={callback.from_user.id}'>"
            f"{callback.from_user.full_name}</a>\n"
            f"🛒 Xizmat: {data.get('service_name')}\n"
            f"🔢 Miqdor: {data.get('quantity'):,}\n"
            f"🔗 Havola: <code>{data.get('link')}</code>\n"
            f"💰 Narx: {total:,} so'm",
            parse_mode="HTML"
        )
    except Exception:
        pass

    await state.clear()
    await callback.message.edit_text(
        f"✅ <b>Buyurtma qabul qilindi!</b>\n\n"
        f"🛒 {data.get('service_name')}\n"
        f"🔢 Miqdor: {data.get('quantity'):,}\n"
        f"💰 To'langan: {total:,} so'm\n\n"
        f"⏳ Buyurtmangiz tez orada bajariladi!",
        parse_mode="HTML"
    )
    await callback.answer("✅ Buyurtma qabul qilindi!")


@router.callback_query(F.data == "cancel_order")
async def cancel_order(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Buyurtma bekor qilindi.")
    await callback.answer()


@router.callback_query(F.data == "noop")
async def noop(callback: CallbackQuery):
    await callback.answer()
