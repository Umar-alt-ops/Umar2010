#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ArsCode — простая консольная система управления интернет-магазином (SQLite + OOP)
Сохраните файл как asrcode.py и запустите: python asrcode.py
"""

import sqlite3
import datetime
from typing import Optional, List, Dict, Any, Tuple

DB_FILE = "arscode.db"

# -------------------------
# Business Exceptions
# -------------------------
class OutOfStockError(Exception):
    pass

class InvalidCouponError(Exception):
    pass

class InsufficientBalanceError(Exception):
    pass

# -------------------------
# Database Manager
# -------------------------
class DatabaseManager:
    def __init__(self, db_file: str = DB_FILE):
        self.conn = sqlite3.connect(db_file)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        cur = self.conn.cursor()
        # categories, products, users, carts, orders, order_items, coupons, coupon_uses, transactions, discounts (simple)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            discount INTEGER DEFAULT 0  -- percent integer
        )""")

        cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category_id INTEGER,
            price INTEGER NOT NULL,
            stock INTEGER DEFAULT 0,
            discount INTEGER DEFAULT 0,  -- percent for product
            FOREIGN KEY(category_id) REFERENCES categories(id)
        )""")

        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            password TEXT,
            balance INTEGER DEFAULT 0,
            is_admin INTEGER DEFAULT 0
        )""")

        cur.execute("""
        CREATE TABLE IF NOT EXISTS carts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(product_id) REFERENCES products(id)
        )""")

        cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            total INTEGER,
            coupon_code TEXT,
            created_at TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )""")

        cur.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            price_at_purchase INTEGER,
            discount_applied INTEGER,
            FOREIGN KEY(order_id) REFERENCES orders(id),
            FOREIGN KEY(product_id) REFERENCES products(id)
        )""")

        cur.execute("""
        CREATE TABLE IF NOT EXISTS coupons (
            code TEXT PRIMARY KEY,
            discount INTEGER,  -- percent
            expires_at TEXT,   -- ISO date
            usage_limit INTEGER,
            used_count INTEGER DEFAULT 0,
            active INTEGER DEFAULT 1
        )""")

        cur.execute("""
        CREATE TABLE IF NOT EXISTS coupon_uses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            coupon_code TEXT,
            user_id INTEGER,
            used_at TEXT,
            FOREIGN KEY(coupon_code) REFERENCES coupons(code),
            FOREIGN KEY(user_id) REFERENCES users(id)
        )""")

        cur.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            order_id INTEGER,
            amount INTEGER,
            type TEXT,
            created_at TEXT
        )""")

        # global discounts (single-record table)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS globals (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            global_discount INTEGER DEFAULT 0
        )""")
        # Ensure one row exists for globals
        cur.execute("INSERT OR IGNORE INTO globals (id, global_discount) VALUES (1, 0)")

        self.conn.commit()

    # Basic helpers
    def execute(self, sql: str, params: tuple = ()):
        cur = self.conn.cursor()
        cur.execute(sql, params)
        self.conn.commit()
        return cur

    def query(self, sql: str, params: tuple = ()):
        cur = self.conn.cursor()
        cur.execute(sql, params)
        return cur.fetchall()

    def close(self):
        self.conn.close()

# -------------------------
# Models & Business Logic
# -------------------------
class Product:
    def __init__(self, db: DatabaseManager, row: sqlite3.Row):
        self.db = db
        self.row = row

    @property
    def id(self): return self.row["id"]
    @property
    def name(self): return self.row["name"]
    @property
    def price(self): return self.row["price"]
    @property
    def stock(self): return self.row["stock"]
    @property
    def discount(self): return self.row["discount"]
    @property
    def category_id(self): return self.row["category_id"]

    def reduce_stock(self, qty: int):
        if self.stock < qty:
            raise OutOfStockError(f"Товар '{self.name}' доступен в количестве {self.stock}, запрошено {qty}")
        self.db.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (qty, self.id))

class User:
    def __init__(self, db: DatabaseManager, row: sqlite3.Row):
        self.db = db
        self.row = row

    @property
    def id(self): return self.row["id"]
    @property
    def name(self): return self.row["name"]
    @property
    def email(self): return self.row["email"]
    @property
    def balance(self): return self.row["balance"]
    @property
    def is_admin(self): return bool(self.row["is_admin"])

    def charge(self, amount: int):
        if self.balance < amount:
            raise InsufficientBalanceError("Недостаточно средств на балансе.")
        self.db.execute("UPDATE users SET balance = balance - ? WHERE id = ?", (amount, self.id))

    def credit(self, amount: int):
        self.db.execute("UPDATE users SET balance = balance + ? WHERE id = ?", (amount, self.id))

# -------------------------
# Discount classes
# -------------------------
class Discount:
    """
    Базовый класс скидки. Реализуем методы:
     - is_valid() : некоторые скидки всегда валидны
     - apply_to_product(product_row) -> percent discount (0-100)
     - apply_to_order(order_amount) -> amount in currency
    """
    def __init__(self, db: DatabaseManager):
        self.db = db

    def is_valid(self) -> bool:
        return True

    def apply_to_product(self, product_row: sqlite3.Row) -> int:
        """Возвращает процент скидки для конкретного товара."""
        raise NotImplementedError

    def apply_to_order(self, order_amount: int) -> int:
        """Возвращает фиксированную сумму скидки на order (если применимо)."""
        return 0

class ProductDiscount(Discount):
    def apply_to_product(self, product_row: sqlite3.Row) -> int:
        return int(product_row["discount"] or 0)

class CategoryDiscount(Discount):
    def apply_to_product(self, product_row: sqlite3.Row) -> int:
        cat_id = product_row["category_id"]
        if not cat_id:
            return 0
        rows = self.db.query("SELECT discount FROM categories WHERE id = ?", (cat_id,))
        if not rows:
            return 0
        return int(rows[0]["discount"] or 0)

class GlobalDiscount(Discount):
    def apply_to_product(self, product_row: sqlite3.Row) -> int:
        rows = self.db.query("SELECT global_discount FROM globals WHERE id = 1")
        return int(rows[0]["global_discount"] or 0)

# -------------------------
# Coupon class
# -------------------------
class Coupon:
    def __init__(self, db: DatabaseManager, code: str):
        self.db = db
        self.code = code.upper()
        row = self.db.query("SELECT * FROM coupons WHERE code = ?", (self.code,))
        if row:
            self.row = row[0]
        else:
            self.row = None

    def exists(self) -> bool:
        return self.row is not None

    def is_active(self) -> bool:
        return bool(self.row["active"]) if self.row else False

    def is_valid(self, user_id: Optional[int] = None) -> Tuple[bool, str]:
        if not self.exists():
            return False, "Купон не найден."
        if not self.is_active():
            return False, "Купон не активен."
        # expiration
        expires = self.row["expires_at"]
        if expires:
            expires_dt = datetime.datetime.fromisoformat(expires)
            if datetime.datetime.now() > expires_dt:
                return False, "Срок действия купона истёк."
        # usage limit
        used = int(self.row["used_count"] or 0)
        limit = int(self.row["usage_limit"] or 0)
        if limit > 0 and used >= limit:
            return False, "Купон исчерпал лимит использования."
        # user-specific: check coupon_uses
        if user_id is not None:
            used_by_user = self.db.query("SELECT 1 FROM coupon_uses WHERE coupon_code = ? AND user_id = ?",
                                        (self.code, user_id))
            if used_by_user:
                return False, "Вы уже использовали этот купон."
        return True, "OK"

    def apply_to_order(self, order_amount: int) -> int:
        """Возвращает сумму скидки (в валюте) для всей суммы заказа."""
        if not self.exists():
            return 0
        percent = int(self.row["discount"] or 0)
        return order_amount * percent // 100

    def mark_used(self, user_id: int):
        self.db.execute("UPDATE coupons SET used_count = used_count + 1 WHERE code = ?", (self.code,))
        self.db.execute("INSERT INTO coupon_uses (coupon_code, user_id, used_at) VALUES (?, ?, ?)",
                        (self.code, user_id, datetime.datetime.now().isoformat()))

# -------------------------
# Shop core
# -------------------------
class Shop:
    def __init__(self, db: DatabaseManager):
        self.db = db
        # discount sources
        self.product_discount = ProductDiscount(db)
        self.category_discount = CategoryDiscount(db)
        self.global_discount = GlobalDiscount(db)

    # ---------- Product & Category ----------
    def add_category(self, name: str, discount: int = 0):
        self.db.execute("INSERT OR IGNORE INTO categories (name, discount) VALUES (?, ?)", (name, discount))

    def add_product(self, name: str, category_name: Optional[str], price: int, stock: int, discount: int = 0):
        cat_id = None
        if category_name:
            rows = self.db.query("SELECT id FROM categories WHERE name = ?", (category_name,))
            if rows:
                cat_id = rows[0]["id"]
            else:
                self.db.execute("INSERT INTO categories (name, discount) VALUES (?, ?)", (category_name, 0))
                rows = self.db.query("SELECT id FROM categories WHERE name = ?", (category_name,))
                cat_id = rows[0]["id"]
        self.db.execute("INSERT INTO products (name, category_id, price, stock, discount) VALUES (?, ?, ?, ?, ?)",
                        (name, cat_id, price, stock, discount))

    def list_products(self) -> List[sqlite3.Row]:
        return self.db.query("""
        SELECT p.*, c.name as category_name FROM products p LEFT JOIN categories c ON p.category_id = c.id
        """)

    # ---------- Users & Auth ----------
    def register_user(self, name: str, email: str, password: str, balance: int = 0, is_admin: bool = False):
        self.db.execute("INSERT INTO users (name, email, password, balance, is_admin) VALUES (?, ?, ?, ?, ?)",
                        (name, email.lower(), password, balance, 1 if is_admin else 0))

    def get_user(self, email: str, password: str) -> Optional[User]:
        rows = self.db.query("SELECT * FROM users WHERE email = ? AND password = ?", (email.lower(), password))
        if rows:
            return User(self.db, rows[0])
        return None

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        rows = self.db.query("SELECT * FROM users WHERE id = ?", (user_id,))
        if rows:
            return User(self.db, rows[0])
        return None

    # ---------- Cart ----------
    def add_to_cart(self, user_id: int, product_id: int, quantity: int):
        # if already in cart, increase
        rows = self.db.query("SELECT id, quantity FROM carts WHERE user_id = ? AND product_id = ?", (user_id, product_id))
        if rows:
            cur_qty = rows[0]["quantity"]
            self.db.execute("UPDATE carts SET quantity = ? WHERE id = ?", (cur_qty + quantity, rows[0]["id"]))
        else:
            self.db.execute("INSERT INTO carts (user_id, product_id, quantity) VALUES (?, ?, ?)",
                            (user_id, product_id, quantity))

    def get_cart(self, user_id: int) -> List[sqlite3.Row]:
        return self.db.query("""
        SELECT c.id as cart_id, p.id as product_id, p.name, p.price, p.discount as product_discount,
               c.quantity, p.stock, p.category_id
        FROM carts c JOIN products p ON c.product_id = p.id
        WHERE c.user_id = ?
        """, (user_id,))

    def clear_cart(self, user_id: int):
        self.db.execute("DELETE FROM carts WHERE user_id = ?", (user_id,))

    # ---------- Pricing & discounts ----------
    def compute_line(self, product_row: sqlite3.Row, quantity: int) -> Dict[str, Any]:
        """
        Возвращает:
            base_price, best_discount_percent, discount_amount, final_price_for_line
        """
        base_price = int(product_row["price"]) * int(quantity)
        # Determine best percent among product, category, global
        p = self.product_discount.apply_to_product(product_row)
        c = self.category_discount.apply_to_product(product_row)
        g = self.global_discount.apply_to_product(product_row)
        best_pct = max(p, c, g)
        discount_amount = base_price * best_pct // 100
        final_price = base_price - discount_amount
        return {
            "base_price": base_price,
            "best_discount_percent": best_pct,
            "discount_amount": discount_amount,
            "final_price": final_price
        }

    def compute_cart_totals(self, user_id: int, coupon_code: Optional[str] = None) -> Dict[str, Any]:
        cart = self.get_cart(user_id)
        subtotal = 0
        details = []
        for row in cart:
            line = self.compute_line(row, row["quantity"])
            subtotal += line["final_price"]
            details.append({
                "product_id": row["product_id"],
                "name": row["name"],
                "quantity": row["quantity"],
                **line
            })
        coupon_discount = 0
        coupon_obj = None
        if coupon_code:
            coupon_obj = Coupon(self.db, coupon_code)
            valid, msg = coupon_obj.is_valid(user_id)
            if not valid:
                raise InvalidCouponError(msg)
            coupon_discount = coupon_obj.apply_to_order(subtotal)
        total = subtotal - coupon_discount
        return {
            "items": details,
            "subtotal": subtotal,
            "coupon_code": coupon_code.upper() if coupon_code else None,
            "coupon_discount": coupon_discount,
            "total": total
        }

    # ---------- Orders & Payments ----------
    def checkout(self, user_id: int, coupon_code: Optional[str] = None) -> int:
        """
        Выполняет оформление заказа:
         - проверяет наличие stock
         - резервирует уменьшением stock
         - снимает деньги с пользователя
         - создает order и order_items
         - добавляет транзакцию и помечает использование купона
        Возвращает id созданного заказа.
        """
        cart_rows = self.get_cart(user_id)
        if not cart_rows:
            raise Exception("Корзина пуста.")

        # 1) Проверка наличия
        for row in cart_rows:
            if row["stock"] < row["quantity"]:
                raise OutOfStockError(f"Товар '{row['name']}' недостаточен в количестве {row['quantity']} (на складе {row['stock']})")

        # 2) Рассчитать сумму и скидку
        totals = self.compute_cart_totals(user_id, coupon_code)
        total_amount = totals["total"]

        # 3) Проверить баланс
        user = self.get_user_by_id(user_id)
        if user.balance < total_amount:
            raise InsufficientBalanceError("Недостаточно средств для оплаты заказа.")

        # 4) Списать баланс
        user.charge(total_amount)

        # 5) Уменьшить stock
        for row in cart_rows:
            prod_row = self.db.query("SELECT * FROM products WHERE id = ?", (row["product_id"],))[0]
            prod = Product(self.db, prod_row)
            prod.reduce_stock(row["quantity"])

        # 6) Создать заказ
        created_at = datetime.datetime.now().isoformat()
        self.db.execute("INSERT INTO orders (user_id, total, coupon_code, created_at) VALUES (?, ?, ?, ?)",
                        (user_id, total_amount, coupon_code.upper() if coupon_code else None, created_at))
        order_id = self.db.query("SELECT last_insert_rowid() as id")[0]["id"]

        # 7) Создать order_items
        for row in cart_rows:
            prod_row = self.db.query("SELECT * FROM products WHERE id = ?", (row["product_id"],))[0]
            line = self.compute_line(prod_row, row["quantity"])
            price_at_purchase = int(prod_row["price"])
            discount_applied = line["best_discount_percent"]
            self.db.execute("""
            INSERT INTO order_items (order_id, product_id, quantity, price_at_purchase, discount_applied)
            VALUES (?, ?, ?, ?, ?)
            """, (order_id, row["product_id"], row["quantity"], price_at_purchase, discount_applied))

        # 8) Записать транзакцию
        self.db.execute("""
        INSERT INTO transactions (user_id, order_id, amount, type, created_at) VALUES (?, ?, ?, ?, ?)
        """, (user_id, order_id, total_amount, "purchase", created_at))

        # 9) Пометить использование купона
        if coupon_code:
            coupon = Coupon(self.db, coupon_code)
            coupon.mark_used(user_id)

        # 10) Очистить корзину
        self.clear_cart(user_id)

        return order_id

    # ---------- Admin reports ----------
    def get_total_revenue(self, period: str = "day") -> int:
        """
        period: 'day', 'week', 'month'
        """
        now = datetime.datetime.now()
        if period == "day":
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "week":
            start = now - datetime.timedelta(days=now.weekday())  # monday
            start = start.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "month":
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            raise ValueError("Unsupported period")
        rows = self.db.query("SELECT SUM(amount) as total FROM transactions WHERE created_at >= ?", (start.isoformat(),))
        return int(rows[0]["total"] or 0)

    def get_top_products(self, limit: int = 3) -> List[Tuple[str,int]]:
        rows = self.db.query("""
        SELECT p.name, SUM(oi.quantity) as sold
        FROM order_items oi JOIN products p ON oi.product_id = p.id
        GROUP BY oi.product_id ORDER BY sold DESC LIMIT ?
        """, (limit,))
        return [(r["name"], r["sold"]) for r in rows]

    def get_coupon_usage(self) -> List[Tuple[str,int]]:
        rows = self.db.query("SELECT code, used_count FROM coupons")
        return [(r["code"], r["used_count"]) for r in rows]

    def get_discount_performance(self) -> List[Tuple[int,int]]:
        """
        Показатель: сколько продаж с какими процентами скидки
        Возвращаем список (discount_percent, count)
        """
        rows = self.db.query("""
        SELECT discount_applied, COUNT(*) as cnt FROM order_items GROUP BY discount_applied ORDER BY discount_applied DESC
        """)
        return [(r["discount_applied"], r["cnt"]) for r in rows]

# -------------------------
# Utilities: initialize sample data
# -------------------------
def bootstrap_sample_data(db: DatabaseManager, shop: Shop):
    # Add categories
    shop.add_category("Молочный шоколад", discount=15)
    shop.add_category("Белый шоколад", discount=15)
    shop.add_category("Горький шоколад", discount=0)

    # Add products
    shop.add_product("Almond Joy", "Молочный шоколад", price=180, stock=50, discount=10)  # product discount 10%
    shop.add_product("White Premium", "Белый шоколад", price=300, stock=30, discount=0)  # category 15%
    shop.add_product("Dark 75%", "Горький шоколад", price=250, stock=40, discount=0)
    shop.add_product("Caramel Bite", "Молочный шоколад", price=150, stock=60, discount=5)

    # Add users
    shop.register_user("Алиса", "client@choco.com", "pass", balance=1500, is_admin=False)
    shop.register_user("Admin", "admin@choco.com", "adminpass", balance=0, is_admin=True)

    # Add coupons: code, discount%, expires, limit
    expires = (datetime.datetime.now() + datetime.timedelta(days=30)).isoformat()
    db.execute("INSERT OR REPLACE INTO coupons (code, discount, expires_at, usage_limit, used_count, active) VALUES (?, ?, ?, ?, ?, ?)",
                ("SWEET15", 15, expires, 100, 0, 1))
    db.execute("INSERT OR REPLACE INTO coupons (code, discount, expires_at, usage_limit, used_count, active) VALUES (?, ?, ?, ?, ?, ?)",
                ("WELCOME10", 10, expires, 1, 0, 1))

    # Set a global discount 5%
    db.execute("UPDATE globals SET global_discount = ? WHERE id = 1", (5,))

# -------------------------
# Minimal Console UI (for demonstration)
# -------------------------
def main():
    db = DatabaseManager()
    shop = Shop(db)

    # bootstrap only if no products exist
    if not db.query("SELECT 1 FROM products LIMIT 1"):
        bootstrap_sample_data(db, shop)

    print("=== Добро пожаловать в ArsCode — магазин шоколада ===")

    current_user: Optional[User] = None

    while True:
        if not current_user:
            print("\n1) Войти\n2) Зарегистрироваться\n3) Выйти")
            choice = input("> ").strip()
            if choice == "1":
                email = input("Email: ").strip()
                pwd = input("Пароль: ").strip()
                user = shop.get_user(email, pwd)
                if user:
                    current_user = user
                    print(f"Добро пожаловать, {current_user.name}! Ваш баланс: {current_user.balance} сом")
                else:
                    print("Неверные учётные данные.")
            elif choice == "2":
                name = input("Имя: ").strip()
                email = input("Email: ").strip()
                pwd = input("Пароль: ").strip()
                try:
                    shop.register_user(name, email, pwd, balance=0, is_admin=False)
                    print("Пользователь зарегистрирован. Войдите.")
                except Exception as e:
                    print("Ошибка при регистрации:", e)
            else:
                print("Выход. Пока!")
                db.close()
                break
        else:
            # logged in
            print("\nМеню:")
            print("1) Каталог")
            print("2) Моя корзина")
            print("3) Мои заказы")
            print("4) Пополнить баланс")
            if current_user.is_admin:
                print("5) Админ-отчёты")
                print("6) Выйти")
            else:
                print("5) Выйти")
            cmd = input("> ").strip()

            if cmd == "1":
                # show products
                prods = shop.list_products()
                print("\nСписок товаров:")
                for p in prods:
                    # compute best discount for display
                    p_disc = int(p["discount"] or 0)
                    cat_disc = shop.category_discount.apply_to_product(p)
                    g_disc = shop.global_discount.apply_to_product(p)
                    best = max(p_disc, cat_disc, g_disc)
                    disc_text = f" (скидка {best}%)" if best else ""
                    print(f"[{p['id']}] {p['name']} — {p['price']} сом{disc_text} — в наличии {p['stock']}")

                pid = input("Добавить товар ID (enter чтобы пропустить): ").strip()
                if pid:
                    try:
                        qty = int(input("Количество: ").strip())
                        shop.add_to_cart(current_user.id, int(pid), qty)
                        print("Добавлено в корзину.")
                    except Exception as e:
                        print("Ошибка:", e)
            elif cmd == "2":
                cart = shop.get_cart(current_user.id)
                if not cart:
                    print("Корзина пуста.")
                else:
                    print("\nВаша корзина:")
                    for c in cart:
                        print(f"- {c['name']} x{c['quantity']} — {c['price']} сом шт.")
                    apply_coupon = input("Применить купон? (код или Enter): ").strip()
                    try:
                        totals = shop.compute_cart_totals(current_user.id, apply_coupon if apply_coupon else None)
                        print(f"Промежуточная сумма: {totals['subtotal']} сом")
                        if totals['coupon_discount']:
                            print(f"Купон {totals['coupon_code']} дал скидку {totals['coupon_discount']} сом")
                        print(f"Итоговая сумма: {totals['total']} сом")
                        ok = input("Оформить заказ? [y/n]: ").strip().lower()
                        if ok == 'y':
                            order_id = shop.checkout(current_user.id, apply_coupon if apply_coupon else None)
                            print(f"Оплата прошла успешно! Номер заказа: {order_id}")
                            # refresh current_user row
                            current_user = shop.get_user_by_id(current_user.id)
                    except InvalidCouponError as e:
                        print("Купон недействителен:", e)
                    except InsufficientBalanceError as e:
                        print("Оплата невозможна:", e)
                    except OutOfStockError as e:
                        print("Ошибка наличия:", e)
                    except Exception as e:
                        print("Ошибка оформления:", e)
            elif cmd == "3":
                rows = db.query("SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC", (current_user.id,))
                if not rows:
                    print("Нет заказов.")
                else:
                    for o in rows:
                        print(f"-- Заказ #{o['id']} — {o['total']} сом — {o['created_at']} (Купон: {o['coupon_code']})")
                        items = db.query("SELECT oi.*, p.name FROM order_items oi JOIN products p ON oi.product_id = p.id WHERE order_id = ?", (o["id"],))
                        for it in items:
                            print(f"   * {it['name']} x{it['quantity']} (цена при покупке {it['price_at_purchase']}, скидка {it['discount_applied']}%)")
            elif cmd == "4":
                amount = input("Сумма пополнения: ").strip()
                try:
                    a = int(amount)
                    db.execute("UPDATE users SET balance = balance + ? WHERE id = ?", (a, current_user.id))
                    current_user = shop.get_user_by_id(current_user.id)
                    print(f"Баланс пополнен. Текущий баланс: {current_user.balance} сом")
                except Exception as e:
                    print("Ошибка:", e)
            elif cmd == "5" and current_user.is_admin:
                print("\nАдмин-отчёты:")
                print("1) Общая прибыль (сегодня/неделя/месяц)")
                print("2) Топ товаров")
                print("3) Использование купонов")
                print("4) Производительность скидок")
                s = input("> ").strip()
                if s == "1":
                    for p in ("day", "week", "month"):
                        print(f"{p}: {shop.get_total_revenue(p)} сом")
                elif s == "2":
                    top = shop.get_top_products(5)
                    for name, sold in top:
                        print(f"{name}: {sold} шт.")
                elif s == "3":
                    for code, used in shop.get_coupon_usage():
                        print(f"{code}: {used} использований")
                elif s == "4":
                    for pct, cnt in shop.get_discount_performance():
                        print(f"Скидка {pct}% — продаж {cnt}")
                else:
                    print("Неверный отчёт.")
            else:
                # exit or non-admin exit
                current_user = None
                print("Вы вышли из аккаунта.")

if __name__ == "__main__":
    main()
