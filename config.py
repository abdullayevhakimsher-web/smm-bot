import os
from dotenv import load_dotenv

load_dotenv()

# ── Bot asosiy sozlamalari ──────────────────────────────────────────────
raw_token = os.getenv("BOT_TOKEN", "").strip()
if raw_token in {"", "YOUR_BOT_TOKEN_HERE"}:
    raw_token = "8676039893:AAEH4PkvSBJ4VTuFqtg5LqFV_eSMJaYjafU"
BOT_TOKEN: str = raw_token

raw_admin = os.getenv("ADMIN_ID", "").strip()
if raw_admin in {"", "YOUR_ADMIN_ID_HERE"}:
    raw_admin = "8811271169"
try:
    ADMIN_ID: int = int(raw_admin)
except ValueError:
    ADMIN_ID: int = 0  # .env faylida ADMIN_ID ni to'g'ri kiriting!
DB_PATH: str = os.getenv("DB_PATH", "smm_bot.db")
REFERRAL_BONUS: int = int(os.getenv("REFERRAL_BONUS", "1000"))

# ── To'lov karta raqamlari ─────────────────────────────────────────────
PAYMENT_CARDS = {
    "click":    os.getenv("CLICK_CARD",   "8600 0000 0000 0000"),
    "payme":    os.getenv("PAYME_CARD",   "8600 0000 0000 0000"),
    "xazna":    os.getenv("XAZNA_CARD",   "8600 0000 0000 0000"),
    "zoomrad":  os.getenv("ZOOMRAD_CARD", "8600 0000 0000 0000"),
    "paynet":   os.getenv("PAYNET_CARD",  "8600 0000 0000 0000"),
    "beepul":   os.getenv("BEEPUL_CARD",  "8600 0000 0000 0000"),
    "oson":     os.getenv("OSON_CARD",    "8600 0000 0000 0000"),
    "uzcard":   os.getenv("UZCARD_CARD",  "8600 0000 0000 0000"),
    "alif":     os.getenv("ALIF_CARD",    "8600 0000 0000 0000"),
    "humo":     os.getenv("HUMO_CARD",    "9860 0000 0000 0000"),
    "bank":     os.getenv("BANK_CARD",    "8600 0000 0000 0000"),
}

# ── Admin buyrug'i paroli ──────────────────────────────────────────────
ADMIN_COMMAND = "Admin11"

# ── Xizmat kategoriyalari ──────────────────────────────────────────────
ORDER_CATEGORIES = {
    "nakrutka": {
        "label": "🚀 Nakrutka",
        "subcategories": ["telegram", "instagram", "youtube", "tiktok", "tekin"],
    },
    "stars": {
        "label": "⭐ Telegram Stars / Premium",
        "subcategories": [],
    },
    "gift": {
        "label": "🎁 Telegram Gift",
        "subcategories": [],
    },
}

NAKRUTKA_SUBCATEGORIES = {
    "telegram":  "📱 Telegram",
    "instagram": "📸 Instagram",
    "youtube":   "▶️ YouTube",
    "tiktok":    "🎵 TikTok",
    "tekin":     "🆓 Tekin Xizmatlar",
}

NUMBER_SERVERS = {
    "server1": "🟢 Server 1 — Barqaror",
    "server2": "⚡ Server 2 — Tezkor",
    "server3": "💚 Server 3 — Tejamkor",
}
