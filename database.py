import aiosqlite
from config import DB_PATH


# ═══════════════════════════════════════════════════════════════════════
#  INIT
# ═══════════════════════════════════════════════════════════════════════
async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                user_id     INTEGER PRIMARY KEY,
                username    TEXT,
                full_name   TEXT,
                balance     INTEGER DEFAULT 0,
                total_deposited INTEGER DEFAULT 0,
                referrer_id INTEGER DEFAULT NULL,
                joined_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS orders (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL,
                category    TEXT NOT NULL,
                subcategory TEXT,
                service_id  INTEGER,
                service_name TEXT,
                quantity    INTEGER DEFAULT 1,
                price       INTEGER DEFAULT 0,
                status      TEXT DEFAULT 'pending',
                link        TEXT,
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            );

            CREATE TABLE IF NOT EXISTS services (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                category    TEXT NOT NULL,
                subcategory TEXT,
                name        TEXT NOT NULL,
                description TEXT,
                price       INTEGER NOT NULL,
                min_qty     INTEGER DEFAULT 1,
                max_qty     INTEGER DEFAULT 10000,
                is_active   INTEGER DEFAULT 1,
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS channels (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id  TEXT NOT NULL UNIQUE,
                channel_name TEXT,
                added_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS messages (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL,
                full_name   TEXT,
                text        TEXT NOT NULL,
                is_read     INTEGER DEFAULT 0,
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS number_services (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                server      TEXT NOT NULL,
                name        TEXT NOT NULL,
                description TEXT,
                price       INTEGER NOT NULL,
                is_active   INTEGER DEFAULT 1,
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS deposits (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL,
                method      TEXT NOT NULL,
                amount      INTEGER NOT NULL,
                status      TEXT DEFAULT 'pending',
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        await db.commit()


# ═══════════════════════════════════════════════════════════════════════
#  USER
# ═══════════════════════════════════════════════════════════════════════
async def get_user(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cur:
            return await cur.fetchone()


async def register_user(user_id: int, username: str, full_name: str, referrer_id: int = None):
    async with aiosqlite.connect(DB_PATH) as db:
        existing = await get_user(user_id)
        if existing:
            await db.execute(
                "UPDATE users SET last_active = CURRENT_TIMESTAMP WHERE user_id = ?",
                (user_id,)
            )
            await db.commit()
            return False  # already existed
        await db.execute(
            "INSERT INTO users (user_id, username, full_name, referrer_id) VALUES (?, ?, ?, ?)",
            (user_id, username, full_name, referrer_id)
        )
        # Referral bonus
        if referrer_id:
            await db.execute(
                "UPDATE users SET balance = balance + ? WHERE user_id = ?",
                (1000, referrer_id)
            )
        await db.commit()
        return True  # new user


async def update_last_active(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET last_active = CURRENT_TIMESTAMP WHERE user_id = ?",
            (user_id,)
        )
        await db.commit()


async def get_user_balance(user_id: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,)) as cur:
            row = await cur.fetchone()
            return row[0] if row else 0


async def add_balance(user_id: int, amount: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET balance = balance + ?, total_deposited = total_deposited + ? WHERE user_id = ?",
            (amount, amount, user_id)
        )
        await db.commit()


async def deduct_balance(user_id: int, amount: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,)) as cur:
            row = await cur.fetchone()
        if not row or row[0] < amount:
            return False
        await db.execute(
            "UPDATE users SET balance = balance - ? WHERE user_id = ?",
            (amount, user_id)
        )
        await db.commit()
        return True


async def count_referrals(user_id: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT COUNT(*) FROM users WHERE referrer_id = ?", (user_id,)
        ) as cur:
            row = await cur.fetchone()
            return row[0] if row else 0


# ═══════════════════════════════════════════════════════════════════════
#  ORDERS
# ═══════════════════════════════════════════════════════════════════════
async def create_order(user_id: int, category: str, subcategory: str,
                       service_id: int, service_name: str,
                       quantity: int, price: int, link: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT INTO orders
               (user_id, category, subcategory, service_id, service_name, quantity, price, link)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (user_id, category, subcategory, service_id, service_name, quantity, price, link)
        )
        await db.commit()


async def get_user_orders(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC LIMIT 20",
            (user_id,)
        ) as cur:
            return await cur.fetchall()


async def count_user_orders(user_id: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT COUNT(*) FROM orders WHERE user_id = ?", (user_id,)
        ) as cur:
            row = await cur.fetchone()
            return row[0] if row else 0


# ═══════════════════════════════════════════════════════════════════════
#  SERVICES
# ═══════════════════════════════════════════════════════════════════════
async def add_service(category: str, subcategory: str, name: str,
                      description: str, price: int, min_qty: int, max_qty: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT INTO services
               (category, subcategory, name, description, price, min_qty, max_qty)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (category, subcategory, name, description, price, min_qty, max_qty)
        )
        await db.commit()


async def get_services(category: str, subcategory: str = None):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        if subcategory:
            async with db.execute(
                "SELECT * FROM services WHERE category=? AND subcategory=? AND is_active=1",
                (category, subcategory)
            ) as cur:
                return await cur.fetchall()
        else:
            async with db.execute(
                "SELECT * FROM services WHERE category=? AND is_active=1", (category,)
            ) as cur:
                return await cur.fetchall()


async def get_service_by_id(service_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM services WHERE id = ?", (service_id,)) as cur:
            return await cur.fetchone()


async def delete_service(service_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE services SET is_active = 0 WHERE id = ?", (service_id,))
        await db.commit()


# ═══════════════════════════════════════════════════════════════════════
#  NUMBER SERVICES
# ═══════════════════════════════════════════════════════════════════════
async def add_number_service(server: str, name: str, description: str, price: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO number_services (server, name, description, price) VALUES (?, ?, ?, ?)",
            (server, name, description, price)
        )
        await db.commit()


async def get_number_services(server: str):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM number_services WHERE server = ? AND is_active = 1", (server,)
        ) as cur:
            return await cur.fetchall()


# ═══════════════════════════════════════════════════════════════════════
#  CHANNELS
# ═══════════════════════════════════════════════════════════════════════
async def add_channel(channel_id: str, channel_name: str):
    async with aiosqlite.connect(DB_PATH) as db:
        try:
            await db.execute(
                "INSERT INTO channels (channel_id, channel_name) VALUES (?, ?)",
                (channel_id, channel_name)
            )
            await db.commit()
            return True
        except Exception:
            return False


async def remove_channel(channel_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM channels WHERE channel_id = ?", (channel_id,))
        await db.commit()


async def get_channels():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM channels") as cur:
            return await cur.fetchall()


# ═══════════════════════════════════════════════════════════════════════
#  MESSAGES (YORDAM)
# ═══════════════════════════════════════════════════════════════════════
async def save_message(user_id: int, full_name: str, text: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO messages (user_id, full_name, text) VALUES (?, ?, ?)",
            (user_id, full_name, text)
        )
        await db.commit()


async def get_unread_messages():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM messages WHERE is_read = 0 ORDER BY created_at DESC"
        ) as cur:
            return await cur.fetchall()


async def get_all_messages():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM messages ORDER BY created_at DESC LIMIT 50"
        ) as cur:
            return await cur.fetchall()


async def mark_message_read(msg_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE messages SET is_read = 1 WHERE id = ?", (msg_id,))
        await db.commit()


# ═══════════════════════════════════════════════════════════════════════
#  STATISTICS
# ═══════════════════════════════════════════════════════════════════════
async def get_stats():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM users") as cur:
            total_users = (await cur.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM orders") as cur:
            total_orders = (await cur.fetchone())[0]
        async with db.execute("SELECT COALESCE(SUM(total_deposited), 0) FROM users") as cur:
            total_deposited = (await cur.fetchone())[0]
        async with db.execute(
            "SELECT COUNT(*) FROM users WHERE last_active >= datetime('now', '-24 hours')"
        ) as cur:
            active_today = (await cur.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM messages WHERE is_read = 0") as cur:
            unread_msgs = (await cur.fetchone())[0]
    return {
        "total_users": total_users,
        "total_orders": total_orders,
        "total_deposited": total_deposited,
        "active_today": active_today,
        "unread_msgs": unread_msgs,
    }


async def get_active_users():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """SELECT user_id, username, full_name, last_active
               FROM users
               WHERE last_active >= datetime('now', '-24 hours')
               ORDER BY last_active DESC"""
        ) as cur:
            return await cur.fetchall()


async def get_all_user_ids():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT user_id FROM users") as cur:
            rows = await cur.fetchall()
            return [r[0] for r in rows]


# ═══════════════════════════════════════════════════════════════════════
#  DEPOSITS
# ═══════════════════════════════════════════════════════════════════════
async def create_deposit(user_id: int, method: str, amount: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO deposits (user_id, method, amount) VALUES (?, ?, ?)",
            (user_id, method, amount)
        )
        await db.commit()


async def get_user_deposits(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT COALESCE(SUM(amount), 0) FROM deposits WHERE user_id = ? AND status = 'confirmed'",
            (user_id,)
        ) as cur:
            row = await cur.fetchone()
            return row[0] if row else 0
