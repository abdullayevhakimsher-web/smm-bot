from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton,
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from config import ORDER_CATEGORIES, NAKRUTKA_SUBCATEGORIES, NUMBER_SERVERS, PAYMENT_CARDS


# ═══════════════════════════════════════════════════════════════════════
#  FOYDALANUVCHI — ASOSIY MENYU
# ═══════════════════════════════════════════════════════════════════════
def main_menu_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="📦 Buyurtma berish"),
        KeyboardButton(text="📋 Buyurtmalarim"),
    )
    builder.row(
        KeyboardButton(text="👤 Hisobim"),
        KeyboardButton(text="📱 Raqam olish"),
    )
    builder.row(
        KeyboardButton(text="💰 Pul ishlash"),
        KeyboardButton(text="💳 Hisob to'ldirish"),
    )
    builder.row(
        KeyboardButton(text="💬 Yordam"),
        KeyboardButton(text="📖 Qo'llanma"),
    )
    return builder.as_markup(resize_keyboard=True)


# ═══════════════════════════════════════════════════════════════════════
#  BUYURTMA — 1-DARAJALI KATEGORIYALAR
# ═══════════════════════════════════════════════════════════════════════
def order_categories_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="🚀 Nakrutka", callback_data="order_cat:nakrutka"))
    builder.row(InlineKeyboardButton(
        text="⭐ Telegram Stars / Premium", callback_data="order_cat:stars"))
    builder.row(InlineKeyboardButton(
        text="🎁 Telegram Gift", callback_data="order_cat:gift"))
    builder.row(InlineKeyboardButton(
        text="🔙 Orqaga", callback_data="back_main"))
    return builder.as_markup()


# ═══════════════════════════════════════════════════════════════════════
#  NAKRUTKA — PLATFORMALAR
# ═══════════════════════════════════════════════════════════════════════
def nakrutka_platforms_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for key, label in NAKRUTKA_SUBCATEGORIES.items():
        builder.row(InlineKeyboardButton(
            text=label, callback_data=f"nakrutka_sub:{key}"))
    builder.row(InlineKeyboardButton(
        text="🔙 Orqaga", callback_data="back_order_cat"))
    return builder.as_markup()


# ═══════════════════════════════════════════════════════════════════════
#  XIZMATLAR RO'YXATI
# ═══════════════════════════════════════════════════════════════════════
def services_list_kb(services: list, back_cb: str = "back_order_cat") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for svc in services:
        builder.row(InlineKeyboardButton(
            text=f"✅ {svc['name']} — {svc['price']:,} so'm",
            callback_data=f"svc:{svc['id']}"
        ))
    if not services:
        builder.row(InlineKeyboardButton(
            text="❌ Hozircha xizmat yo'q", callback_data="noop"))
    builder.row(InlineKeyboardButton(text="🔙 Orqaga", callback_data=back_cb))
    return builder.as_markup()


# ═══════════════════════════════════════════════════════════════════════
#  RAQAM OLISH — SERVERLAR
# ═══════════════════════════════════════════════════════════════════════
def number_servers_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for key, label in NUMBER_SERVERS.items():
        builder.row(InlineKeyboardButton(
            text=label, callback_data=f"numserver:{key}"))
    builder.row(InlineKeyboardButton(
        text="🔙 Orqaga", callback_data="back_main"))
    return builder.as_markup()


def number_services_kb(services: list, server_key: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for svc in services:
        builder.row(InlineKeyboardButton(
            text=f"📞 {svc['name']} — {svc['price']:,} so'm",
            callback_data=f"numsvc:{svc['id']}"
        ))
    if not services:
        builder.row(InlineKeyboardButton(
            text="❌ Hozircha xizmat yo'q", callback_data="noop"))
    builder.row(InlineKeyboardButton(
        text="🔙 Orqaga", callback_data="back_num_servers"))
    return builder.as_markup()


# ═══════════════════════════════════════════════════════════════════════
#  HISOB TO'LDIRISH — TO'LOV USULLARI
# ═══════════════════════════════════════════════════════════════════════
def topup_methods_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    methods = [
        ("💳 Click [avto]",    "topup:click"),
        ("💳 Payme [avto]",    "topup:payme"),
        ("💳 Xazna [avto]",    "topup:xazna"),
        ("💳 Zoomrad [avto]",  "topup:zoomrad"),
        ("💳 Paynet [avto]",   "topup:paynet"),
        ("💳 Beepul [avto]",   "topup:beepul"),
        ("💳 Oson [avto]",     "topup:oson"),
        ("🏧 UzCard [avto]",   "topup:uzcard"),
        ("💳 Alif [avto]",     "topup:alif"),
        ("🏧 Humo [avto]",     "topup:humo"),
        ("🏦 Bank karta [avto]","topup:bank"),
        ("📩 Adminga murojat", "topup:admin"),
    ]
    for label, cb in methods:
        builder.row(InlineKeyboardButton(text=label, callback_data=cb))
    builder.row(InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_main"))
    return builder.as_markup()


# ═══════════════════════════════════════════════════════════════════════
#  YORDAM
# ═══════════════════════════════════════════════════════════════════════
def help_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="💬 Admin bilan chat", callback_data="help_admin_chat"))
    builder.row(InlineKeyboardButton(
        text="❓ Ko'p beriladigan savollar (FAQ)", callback_data="help_faq"))
    builder.row(InlineKeyboardButton(
        text="🔙 Orqaga", callback_data="back_main"))
    return builder.as_markup()


# ═══════════════════════════════════════════════════════════════════════
#  ADMIN — ASOSIY MENYU
# ═══════════════════════════════════════════════════════════════════════
def admin_main_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📊 Statistika", callback_data="adm:stats"),
        InlineKeyboardButton(text="👥 Faol userlar", callback_data="adm:users"),
    )
    builder.row(
        InlineKeyboardButton(text="📢 Kanal qo'shish", callback_data="adm:add_channel"),
        InlineKeyboardButton(text="🔕 Kanalni o'chirish", callback_data="adm:del_channel"),
    )
    builder.row(
        InlineKeyboardButton(text="💬 Murojatlar", callback_data="adm:messages"),
    )
    builder.row(
        InlineKeyboardButton(text="➕ Xizmat qo'shish", callback_data="adm:add_service"),
        InlineKeyboardButton(text="🗑 Xizmat o'chirish", callback_data="adm:del_service"),
    )
    builder.row(
        InlineKeyboardButton(text="📱 Raqam xizmati qo'sh", callback_data="adm:add_num_service"),
    )
    return builder.as_markup()


# ═══════════════════════════════════════════════════════════════════════
#  ADMIN — KATEGORIYA TANLASH (xizmat qo'shish uchun)
# ═══════════════════════════════════════════════════════════════════════
def admin_service_cat_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="🚀 Nakrutka", callback_data="admsvc_cat:nakrutka"))
    builder.row(InlineKeyboardButton(
        text="⭐ Stars / Premium", callback_data="admsvc_cat:stars"))
    builder.row(InlineKeyboardButton(
        text="🎁 Telegram Gift", callback_data="admsvc_cat:gift"))
    builder.row(InlineKeyboardButton(
        text="🔙 Orqaga", callback_data="adm:back"))
    return builder.as_markup()


def admin_nakrutka_sub_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for key, label in NAKRUTKA_SUBCATEGORIES.items():
        builder.row(InlineKeyboardButton(
            text=label, callback_data=f"admsvc_sub:{key}"))
    builder.row(InlineKeyboardButton(
        text="🔙 Orqaga", callback_data="adm:add_service"))
    return builder.as_markup()


def admin_servers_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for key, label in NUMBER_SERVERS.items():
        builder.row(InlineKeyboardButton(
            text=label, callback_data=f"admnum_srv:{key}"))
    builder.row(InlineKeyboardButton(
        text="🔙 Orqaga", callback_data="adm:back"))
    return builder.as_markup()


# ═══════════════════════════════════════════════════════════════════════
#  UNIVERSAL — Orqaga
# ═══════════════════════════════════════════════════════════════════════
def back_kb(callback_data: str = "back_main") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔙 Orqaga", callback_data=callback_data))
    return builder.as_markup()


def confirm_order_kb(service_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"confirm_order:{service_id}"),
        InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_order"),
    )
    return builder.as_markup()


def cancel_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="❌ Bekor qilish"))
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
