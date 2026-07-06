import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import  BOT_TOKEN, ADMIN_ID
import database as db

# User handlers
from handlers.user import start, order, my_orders, balance, topup, earn, number, help, guide

# Admin handlers
from handlers.admin import panel, stats, channels, services, messages, users

import os
import asyncio
from aiogram import Bot, Dispatcher
from aiohttp import web  # Port ochish uchun ushbu kutubxona shart!

# ... sizning boshqa importlaringiz va bot/dp sozlamalaringiz ...

# Render tekshirganda "OK" javobini qaytaradigan funksiya
async def handle(request):
    return web.Response(text="SUPER SMM BOT muvaffaqiyatli ishlamoqda!")

async def main():
    # 1. RENDER UCHUN PORT BINDING (Buni poolingdan oldin qo'shish shart!)
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"Render veb-serveri {port}-portda ishga tushdi.")

    # 2. SIZNING BOTINGIZNI ISHGA TUSHIRISH KODLARI (O'ziniki qoladi)
    # logger.info("Ma'lumotlar bazasi tayyor.")
    # logger.info("SMM Bot ishga tushdi!")
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

# ── Logging ───────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


async def main():
    # ── Ma'lumotlar bazasini yaratish ──────────────────────────────────
    await db.init_db()
    logger.info("✅ Ma'lumotlar bazasi tayyor.")

    # ── Bot va Dispatcher ──────────────────────────────────────────────
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=MemoryStorage())

    # ── Routerlarni ulash (tartib muhim!) ─────────────────────────────

    # Admin handlerlari (avval, chunki ular aniq komandalar)
    dp.include_router(panel.router)
    dp.include_router(stats.router)
    dp.include_router(channels.router)
    dp.include_router(services.router)
    dp.include_router(messages.router)
    dp.include_router(users.router)

    # Foydalanuvchi handlerlari
    dp.include_router(start.router)
    dp.include_router(order.router)
    dp.include_router(my_orders.router)
    dp.include_router(balance.router)
    dp.include_router(topup.router)
    dp.include_router(earn.router)
    dp.include_router(number.router)
    dp.include_router(help.router)
    dp.include_router(guide.router)

    # ── Botni ishga tushirish ──────────────────────────────────────────
    logger.info(f"🚀 SMM Bot ishga tushdi! Admin ID: {ADMIN_ID}")

    try:
        await bot.send_message(
            ADMIN_ID,
            "✅ <b>SMM Bot ishga tushdi!</b>\n\n"
            "🤖 Bot muvaffaqiyatli ishga tushdi.\n"
            
        )
    except Exception:
        logger.warning("Admin ga xabar yuborib bo'lmadi (ID to'g'riligini tekshiring)")

    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
