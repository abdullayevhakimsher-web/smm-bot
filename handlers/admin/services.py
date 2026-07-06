from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

import database as db
from keyboards import (
    admin_service_cat_kb, admin_nakrutka_sub_kb,
    admin_servers_kb, cancel_kb
)
from config import ADMIN_ID, NAKRUTKA_SUBCATEGORIES

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


class ServiceStates(StatesGroup):
    # Xizmat qo'shish
    choosing_cat = State()
    choosing_sub = State()
    waiting_name = State()
    waiting_desc = State()
    waiting_price = State()
    waiting_min = State()
    waiting_max = State()
    # Raqam xizmati
    choosing_num_server = State()
    waiting_num_name = State()
    waiting_num_desc = State()
    waiting_num_price = State()


# ═══════════════════════════════════════════════════════════════════════
#  XIZMAT QO'SHISH
# ═══════════════════════════════════════════════════════════════════════
@router.callback_query(F.data == "adm:add_service")
async def admin_add_service(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    await callback.message.edit_text(
        "➕ <b>Xizmat qo'shish</b>\n\nKategoriyani tanlang:",
        parse_mode="HTML",
        reply_markup=admin_service_cat_kb()
    )
    await state.set_state(ServiceStates.choosing_cat)
    await callback.answer()


@router.callback_query(F.data.startswith("admsvc_cat:"))
async def admin_svc_category(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    cat = callback.data.split(":")[1]
    await state.update_data(category=cat, subcategory=None)

    if cat == "nakrutka":
        await callback.message.edit_text(
            "➕ <b>Nakrutka</b>\n\nPlatformani tanlang:",
            parse_mode="HTML",
            reply_markup=admin_nakrutka_sub_kb()
        )
        await state.set_state(ServiceStates.choosing_sub)
    else:
        await callback.message.edit_text(
            f"➕ <b>Xizmat nomi:</b>\n\nNomni kiriting:",
            parse_mode="HTML"
        )
        await callback.message.answer("Yoki:", reply_markup=cancel_kb())
        await state.set_state(ServiceStates.waiting_name)
    await callback.answer()


@router.callback_query(F.data.startswith("admsvc_sub:"))
async def admin_svc_subcategory(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    sub = callback.data.split(":")[1]
    await state.update_data(subcategory=sub)
    label = NAKRUTKA_SUBCATEGORIES.get(sub, sub)
    await callback.message.edit_text(
        f"➕ Nakrutka → {label}\n\n<b>Xizmat nomini kiriting:</b>",
        parse_mode="HTML"
    )
    await callback.message.answer("Bekor qilish:", reply_markup=cancel_kb())
    await state.set_state(ServiceStates.waiting_name)
    await callback.answer()


@router.message(ServiceStates.waiting_name, F.text == "❌ Bekor qilish")
async def cancel_svc_name(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Bekor qilindi.")


@router.message(ServiceStates.waiting_name)
async def svc_name(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.update_data(name=message.text.strip())
    await message.answer("📝 <b>Tavsif kiriting</b> (yoki <i>yo'q</i> deb yozing):", parse_mode="HTML")
    await state.set_state(ServiceStates.waiting_desc)


@router.message(ServiceStates.waiting_desc)
async def svc_desc(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    desc = message.text.strip()
    if desc.lower() in ("yo'q", "yoq", "-", "none"):
        desc = ""
    await state.update_data(description=desc)
    await message.answer("💰 <b>Narxini kiriting</b> (so'mda, faqat raqam):", parse_mode="HTML")
    await state.set_state(ServiceStates.waiting_price)


@router.message(ServiceStates.waiting_price)
async def svc_price(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    if not message.text.replace(" ", "").isdigit():
        await message.answer("⚠️ Faqat raqam kiriting!")
        return
    await state.update_data(price=int(message.text.replace(" ", "")))
    await message.answer("📊 <b>Minimal miqdorni kiriting</b> (masalan: 100):", parse_mode="HTML")
    await state.set_state(ServiceStates.waiting_min)


@router.message(ServiceStates.waiting_min)
async def svc_min(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    if not message.text.isdigit():
        await message.answer("⚠️ Faqat raqam kiriting!")
        return
    await state.update_data(min_qty=int(message.text))
    await message.answer("📊 <b>Maksimal miqdorni kiriting</b> (masalan: 10000):", parse_mode="HTML")
    await state.set_state(ServiceStates.waiting_max)


@router.message(ServiceStates.waiting_max)
async def svc_max(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    if not message.text.isdigit():
        await message.answer("⚠️ Faqat raqam kiriting!")
        return

    data = await state.get_data()
    max_qty = int(message.text)

    await db.add_service(
        category=data.get("category", ""),
        subcategory=data.get("subcategory"),
        name=data["name"],
        description=data.get("description", ""),
        price=data["price"],
        min_qty=data.get("min_qty", 1),
        max_qty=max_qty
    )

    await state.clear()
    await message.answer(
        f"✅ <b>Xizmat qo'shildi!</b>\n\n"
        f"📋 <b>Nom:</b> {data['name']}\n"
        f"💰 <b>Narx:</b> {data['price']:,} so'm\n"
        f"📊 <b>Min/Max:</b> {data.get('min_qty', 1)} / {max_qty}",
        parse_mode="HTML"
    )


# ═══════════════════════════════════════════════════════════════════════
#  RAQAM XIZMATI QO'SHISH
# ═══════════════════════════════════════════════════════════════════════
@router.callback_query(F.data == "adm:add_num_service")
async def admin_add_num_service(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    await callback.message.edit_text(
        "📱 <b>Raqam xizmati qo'shish</b>\n\nServerni tanlang:",
        parse_mode="HTML",
        reply_markup=admin_servers_kb()
    )
    await state.set_state(ServiceStates.choosing_num_server)
    await callback.answer()


@router.callback_query(F.data.startswith("admnum_srv:"))
async def admin_num_server(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    server = callback.data.split(":")[1]
    await state.update_data(server=server)
    await callback.message.edit_text(
        f"📱 <b>Server: {server}</b>\n\nXizmat nomini kiriting:",
        parse_mode="HTML"
    )
    await callback.message.answer("Bekor qilish:", reply_markup=cancel_kb())
    await state.set_state(ServiceStates.waiting_num_name)
    await callback.answer()


@router.message(ServiceStates.waiting_num_name, F.text == "❌ Bekor qilish")
async def cancel_num_service(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Bekor qilindi.")


@router.message(ServiceStates.waiting_num_name)
async def num_svc_name(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.update_data(name=message.text.strip())
    await message.answer("📝 Tavsif kiriting (yoki <i>yo'q</i>):", parse_mode="HTML")
    await state.set_state(ServiceStates.waiting_num_desc)


@router.message(ServiceStates.waiting_num_desc)
async def num_svc_desc(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    desc = message.text.strip()
    if desc.lower() in ("yo'q", "yoq", "-"):
        desc = ""
    await state.update_data(description=desc)
    await message.answer("💰 Narxini kiriting (so'mda):")
    await state.set_state(ServiceStates.waiting_num_price)


@router.message(ServiceStates.waiting_num_price)
async def num_svc_price(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    if not message.text.replace(" ", "").isdigit():
        await message.answer("⚠️ Faqat raqam kiriting!")
        return
    data = await state.get_data()
    price = int(message.text.replace(" ", ""))

    await db.add_number_service(
        server=data["server"],
        name=data["name"],
        description=data.get("description", ""),
        price=price
    )
    await state.clear()
    await message.answer(
        f"✅ <b>Raqam xizmati qo'shildi!</b>\n\n"
        f"🖥 Server: {data['server']}\n"
        f"📋 Nom: {data['name']}\n"
        f"💰 Narx: {price:,} so'm",
        parse_mode="HTML"
    )


# ═══════════════════════════════════════════════════════════════════════
#  XIZMAT O'CHIRISH
# ═══════════════════════════════════════════════════════════════════════
@router.callback_query(F.data == "adm:del_service")
async def admin_del_service(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return

    # Barcha faol xizmatlar
    import aiosqlite
    from config import DB_PATH
    async with aiosqlite.connect(DB_PATH) as dbc:
        dbc.row_factory = aiosqlite.Row
        async with dbc.execute(
            "SELECT * FROM services WHERE is_active = 1 LIMIT 30"
        ) as cur:
            services = await cur.fetchall()

    builder = InlineKeyboardBuilder()
    for svc in services:
        builder.row(InlineKeyboardButton(
            text=f"🗑 {svc['name']} ({svc['category']})",
            callback_data=f"delsvc:{svc['id']}"
        ))
    if not services:
        builder.row(InlineKeyboardButton(text="❌ Xizmatlar yo'q", callback_data="noop"))
    builder.row(InlineKeyboardButton(text="🔙 Orqaga", callback_data="adm:back"))

    await callback.message.edit_text(
        "🗑 <b>O'chirish uchun xizmatni tanlang:</b>",
        parse_mode="HTML",
        reply_markup=builder.as_markup()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("delsvc:"))
async def delete_service(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    svc_id = int(callback.data.split(":")[1])
    await db.delete_service(svc_id)
    await callback.answer("✅ Xizmat o'chirildi!", show_alert=True)
    # Ro'yxatni yangilash
    await admin_del_service(callback)
