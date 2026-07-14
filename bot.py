import asyncio
import logging
import os

from aiohttp import web, TCPConnector
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

import database as db
from config import BOT_TOKEN, ADMIN_ID

# User handlers
from handlers.user import start, order, my_orders, balance, topup, earn, number, help, guide

# Admin handlers
from handlers.admin import panel, stats, channels, services, messages, users

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


async def wait_for_telegram_connection(max_retries=5):
    """Retry connection to Telegram with exponential backoff"""
    connector = TCPConnector(
        limit=100,
        limit_per_host=30,
        ttl_dns_cache=300,
        enable_cleanup_closed=True,
    )
    
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Telegram API ga ulanish sinov #{attempt + 1}...")
            user = await bot.get_me()
            logger.info(f"✅ Telegram API bilan ulanish muvaffaqiyatli: {user.first_name}")
            return bot
        except Exception as e:
            wait_time = 2 ** attempt  # Exponential backoff: 1, 2, 4, 8, 16 seconds
            logger.warning(f"❌ Telegram API bilan ulanib bo'lmadi: {e}")
            
            if attempt < max_retries - 1:
                logger.info(f"⏳ {wait_time} soniyadan keyin qayta urinish...")
                await asyncio.sleep(wait_time)
            else:
                logger.error("❌ Maksimal urinishlar tugadi. Iltimos, internet ulanishingizni tekshiring.")
                raise
    
    return bot


async def handle(request):
    return web.Response(text="SUPER SMM BOT muvaffaqiyatli ishlamoqda!")


async def create_render_site(runner, default_port=10000, max_attempts=5):
    raw_port = os.environ.get("PORT")
    base_port = int(raw_port) if raw_port is not None else default_port
    allow_fallback = raw_port is None

    for offset in range(max_attempts if allow_fallback else 1):
        port = base_port + offset
        site = web.TCPSite(runner, "0.0.0.0", port)
        try:
            await site.start()
            logger.info(f"Render veb-serveri {port}-portda ishga tushdi.")
            return site, port
        except OSError as e:
            if e.errno == 10048:
                if allow_fallback:
                    logger.warning(f"Port {port} band; {port + 1} portga o'tish sinovi...")
                    continue
                raise RuntimeError(
                    f"Port {port} band. Agar PORT muhit o'zgaruvchisi o'rnatilgan bo'lsa, boshqa portni tanlang."
                ) from e
            raise

    raise RuntimeError(
        f"Portlar {base_port}-{base_port + max_attempts - 1} band. Iltimos, birini bo'shating yoki .env faylida boshqa PORT kiriting."
    )


async def main():
    await db.init_db()
    logger.info("✅ Ma'lumotlar bazasi tayyor.")

    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()

    site, port = await create_render_site(runner)

    # Telegram API ga ulana olguncha kutish
    bot = await wait_for_telegram_connection()
    
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(panel.router)
    dp.include_router(stats.router)
    dp.include_router(channels.router)
    dp.include_router(services.router)
    dp.include_router(messages.router)
    dp.include_router(users.router)

    dp.include_router(start.router)
    dp.include_router(order.router)
    dp.include_router(my_orders.router)
    dp.include_router(balance.router)
    dp.include_router(topup.router)
    dp.include_router(earn.router)
    dp.include_router(number.router)
    dp.include_router(help.router)
    dp.include_router(guide.router)

    logger.info(f"🚀 SMM Bot ishga tushdi! Admin ID: {ADMIN_ID}")

    try:
        await bot.send_message(
            ADMIN_ID,
            "✅ <b>SMM Bot ishga tushdi!</b>\n\n"
            "🤖 Bot muvaffaqiyatli ishga tushdi."
        )
    except Exception:
        logger.warning("Admin ga xabar yuborib bo'lmadi (ID to'g'riligini tekshiring)")

    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
