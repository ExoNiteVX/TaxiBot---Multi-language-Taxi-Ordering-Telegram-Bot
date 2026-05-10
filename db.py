import sqlite3

DB_NAME = 'taxi.db'

def connect():
    return sqlite3.connect(DB_NAME)

def create_all_tables():
    with connect() as con:
        con.execute("""
        CREATE TABLE IF NOT EXISTS users (
            tg_id INTEGER PRIMARY KEY,
            full_name TEXT,
            phone TEXT,
            lat REAL,
            long REAL,
            lang TEXT DEFAULT 'uz'
        )
        """)

        con.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tg_id INTEGER,
            pickup_lat REAL,
            pickup_lon REAL,
            dest_lat REAL,
            dest_lon REAL,
            tariff TEXT,
            price INTEGER,
            status TEXT DEFAULT 'jarayonda',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        con.execute("""
        CREATE TABLE IF NOT EXISTS fares (
            tariff_type TEXT PRIMARY KEY,
            base_price INTEGER,
            per_km INTEGER
        )
        """)
        con.execute("INSERT OR IGNORE INTO fares VALUES ('ekonom', 6000, 2000)")
        con.execute("INSERT OR IGNORE INTO fares VALUES ('comfort', 10000, 3000)")

        con.execute("""
        CREATE TABLE IF NOT EXISTS promocodes (
            code TEXT PRIMARY KEY,
            discount_percentage INTEGER,
            max_uses INTEGER,
            used_count INTEGER DEFAULT 0
        )
        """)

        con.execute("""
        CREATE TABLE IF NOT EXISTS drivers (
            tg_id INTEGER PRIMARY KEY,
            full_name TEXT,
            car_model TEXT,
            car_number TEXT,
            status TEXT DEFAULT 'jarayonda'
        )
        """)

def add_user(tg_id, name, phone, lat, lon, lang='uz'):
    with connect() as con:
        con.execute("""
            INSERT OR REPLACE INTO users (tg_id, full_name, phone, lat, long, lang)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (tg_id, name, phone, lat, lon, lang))

def get_user(tg_id):
    with connect() as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM users WHERE tg_id = ?", (tg_id,))
        return cur.fetchone()

def add_order(tg_id, p_lat, p_lon, d_lat, d_lon, tariff, price):
    with connect() as con:
        con.execute("""
        INSERT INTO orders (tg_id, pickup_lat, pickup_lon, dest_lat, dest_lon, tariff, price)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (tg_id, p_lat, p_lon, d_lat, d_lon, tariff, price))

def add_pending_driver(tg_id, name, model, number):
    with connect() as con:
        con.execute("""
            INSERT OR REPLACE INTO drivers (tg_id, full_name, car_model, car_number, status)
            VALUES (?, ?, ?, ?, 'jarayonda')
        """, (tg_id, name, model, number))

def is_active_driver(tg_id):
    with connect() as con:
        res = con.execute(
            "SELECT 1 FROM drivers WHERE tg_id = ? AND status = 'aktiv'", (tg_id,)
        ).fetchone()
        return res is not None

def update_driver_status(tg_id, status):
    with connect() as con:
        con.execute("UPDATE drivers SET status = ? WHERE tg_id = ?", (status, tg_id))

def get_driver_full_info(tg_id):
    with connect() as con:
        return con.execute(
            "SELECT full_name, car_model, car_number FROM drivers WHERE tg_id = ?",
            (tg_id,)
        ).fetchone()

def update_order_status(customer_id, new_status):
    with connect() as con:
        con.execute("""
            UPDATE orders SET status = ? 
            WHERE id = (
                SELECT id FROM orders 
                WHERE tg_id = ? AND status NOT IN ('Yakunlandi', 'Bekor qilindi') 
                ORDER BY id DESC LIMIT 1
            )
        """, (new_status, customer_id))

def update_user_lang(tg_id, lang):
    with connect() as con:
        con.execute("UPDATE users SET lang = ? WHERE tg_id = ?", (lang, tg_id))

def get_stats():
    with connect() as con:
        user_count = con.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        order_count = con.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
        return user_count, order_count

def get_daily_stats():
    with connect() as con:
        return con.execute("""
            SELECT date(created_at) as day, COUNT(*), SUM(price)
            FROM orders WHERE status = 'Yakunlandi'
            GROUP BY day ORDER BY day DESC LIMIT 7
        """).fetchall()

def get_fare_settings(tariff_type):
    with connect() as con:
        return con.execute("SELECT base_price, per_km FROM fares WHERE tariff_type = ?", (tariff_type,)).fetchone()

def get_all_user_ids():
    with connect() as con:
        return [row[0] for row in con.execute("SELECT tg_id FROM users").fetchall()]

def check_promo_db(code):
    with connect() as con:
        cur = con.cursor()
        cur.execute("SELECT discount_percentage FROM promocodes WHERE code = ? AND used_count < max_uses", (code.upper(),))
        return cur.fetchone()

def use_promo_db(code):
    with connect() as con:
        con.execute("UPDATE promocodes SET used_count = used_count + 1 WHERE code = ?", (code.upper(),))

def edit_name(new_name, tg_id):
    with connect() as con:
        con.execute("UPDATE users SET full_name = ? WHERE tg_id = ?", (new_name, tg_id))

def edit_phone(new_phone, tg_id):
    with connect() as con:
        con.execute("UPDATE users SET phone = ? WHERE tg_id = ?", (new_phone, tg_id))

def add_promocode_db(code, discount, max_uses):
    with connect() as con:
        con.execute("""
            INSERT OR REPLACE INTO promocodes (code, discount_percentage, max_uses, used_count)
            VALUES (?, ?, ?, 0)
        """, (code.upper(), discount, max_uses))

def show_history_db(tg_id):
    with connect() as con:
        return con.execute("""
            SELECT tariff, price, status, created_at 
            FROM orders 
            WHERE tg_id = ? 
            ORDER BY id DESC LIMIT 5
        """, (tg_id,)).fetchall()

def update_fare(tariff_type, base_price, per_km):
    with connect() as con:
        con.execute("""
            UPDATE fares 
            SET base_price = ?, per_km = ? 
            WHERE tariff_type = ?
        """, (base_price, per_km, tariff_type))

def admin_add_driver_db(tg_id, name, model, number):
    with connect() as con:
        con.execute("""
            INSERT OR REPLACE INTO drivers (tg_id, full_name, car_model, car_number, status)
            VALUES (?, ?, ?, ?, 'aktiv')
        """, (tg_id, name, model, number))