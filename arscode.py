import sqlite3
from datetime import datetime
conn = sqlite3.connect('chocolate.db')
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT UNIQUE,
    password TEXT,
    balance REAL DEFAULT 0,
    role TEXT CHECK(role IN ('client', 'admin'))
)
''')
conn.commit()
cursor.execute('''
CREATE TABLE IF NOT EXISTS products (
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
category TEXT,
price REAL,
quantity INTEGER,
discount_id INTEGER NULL,
FOREIGN KEY(discount_id) REFERENCES discounts(id))
'''
)
conn.commit()
cursor.execute('''
CREATE TABLE IF NOT EXISTS discounts (
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
discount_percent REAL,
valid_from TEXT,
valid_to TEXT, 
is_active INTEGER DEFAULT 1,
applies_to TEXT CHECK(applies_to IN ('product', 'category', 'global')),
target_value TEXT NULL
)
'''
)

conn.commit()

cursor.execute('''
CREATE TABLE IF NOT EXISTS coupons (
id INTEGER PRIMARY KEY AUTOINCREMENT,
code TEXT UNIQUE,
discount_percent REAL,
valid_from TEXT Дата,
valid_to TEXT,
usage_limit INTEGER,
used_count INTEGER DEFAULT 0,
is_active INTEGER DEFAULT 1
)
''')
conn.commit()
cursor.execute('''
CREATE TABLE IF NOT EXISTS orders (
d INTEGER PRIMARY KEY AUTOINCREMENT, 
user_id INTEGER,
total_price REAL,
coupon_id INTEGER NULL, 
created_at TEXT, 
status TEXT CHECK(status IN ('pending', 'paid', 'shipped', 'completed', 'cancelled')),
FOREIGN KEY(user_id) REFERENCES users(id),
FOREIGN KEY(coupon_id) REFERENCES coupons(id)
)
''')
conn.commit()
cursor.execute('''
CREATE TABLE IF NOT EXISTS order_items (
id INTEGER PRIMARY KEY AUTOINCREMENT,
order_id INTEGER,
product_id INTEGER,
quantity INTEGER,
price REAL,
FOREIGN KEY(order_id) REFERENCES orders(id),
FOREIGN KEY(product_id) REFERENCES products(id)
)
''')
conn.commit()

cursor.execute('''
CREATE TABLE IF NOT EXISTS payments (
id INTEGER PRIMARY KEY AUTOINCREMENT,
order_id INTEGER, 
user_id INTEGER,
amount REAL, 
status TEXT CHECK(status IN ('success', 'failed')),
payment_date TEXT,
FOREIGN KEY(order_id) REFERENCES orders(id),
FOREIGN KEY(user_id) REFERENCES users(id)
)
''')
conn.commit()


class OutOfStockError(Exception):
    pass
class InvalidCouponError(Exception):
    pass
class InsufficientBalanceError(Exception):
    pass

class User:
    def __init__(self, db, name, email, password, balance=0):
        self.db = db
        self.name = name
        self.email = email
        self.password = password
        self.balance = balance
    
def save(self):
        cursor = self.db.cursor()
        try:
            cursor.execute('INSERT INTO users (name, email, password, balance) VALUES (?, ?, ?, ?)',
                           (self.name, self.email, self.password, self.balance))
            self.db.commit()
            print(" Пользователь успешно зарегистрирован!")
        except sqlite3.IntegrityError:
            print("⚠️ Пользователь с таким email уже существует.")
def login(db, email, password):
    cursor = db.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password))
    user = cursor.fetchone()
    if user:
        print(f" Добро пожаловать, {user[1]}!")
        return user
    else:
        print(" Неверный email или пароль.")
        return None


def run():
    db = sqlite3.connect('chocolate.db')
    print("=== Добро пожаловать в ChocolateHeaven ===")

    while True:
        print("\nМеню:")
        print("1 — Войти")
        print("2 — Зарегистрироваться")
        print("3 — Выйти")

        choice = input("Выберите действие: ")

        if choice == '1':
            email = input("Введите email: ")
            password = input("Введите пароль: ")
            login(db, email, password)

        elif choice == '2':
            name = input("Введите имя: ")
            email = input("Введите email: ")
            password = input("Введите пароль: ")
            user = User(db, name, email, password)
            user.save()

        elif choice == '3':
            print("👋 До свидания!")
            break
        else:
            print("⚠️ Неверный выбор, попробуйте снова.")



class DatabaseManager:
    def __init__(self, db_file: str = 'chocolate.db'):
        self.conn = sqlite3.connect(db_file)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        cur = self.conn.cursor()

cursor.execute("INSERT INTO discounts (name, discount_percent, valid_from, valid_to, is_active, applies_to, target_value) VALUES (?, ?, ?, ?, ?, ?, ?)",
('Summer Sale', 15.0, '2024-06-01', '2024-06-30', 1, 'category', 'chocolate'))

conn.commit()

class Discount:
    def __init__(self):
        pass

    def is_valid(self):
        pass
    
    def apply_product(self, product):
        self.product = product
        pass

    def apply_order(self, order):
        self.order = order
        pass

class Coupon:
    def __init__(self):
        pass

    def is_valid(self):
        pass
    
    def apply_product(self, product):
        self.product = product
        pass

    def apply_order(self, order):
        self.order = order
        pass
# Для админимистратора: получение общей выручки за указанный период
def get_total_revenue(period: str):
    conn = sqlite3.connect('chocolate.db')
    cursor = conn.cursor()
    query = '''
    SELECT SUM(amount) as total_revenue
    FROM payments
    WHERE status = 'success' AND payment_date >= date('now', ?)
    '''
    if period == 'daily':
        time_frame = '-1 day'
    elif period == 'monthly':
        time_frame = '-1 month'
    elif period == 'yearly':
        time_frame = '-1 year'
    else:
        raise ValueError("Invalid period. Choose from 'daily', 'monthly', 'yearly'.")
    
    cursor.execute(query, (time_frame,))
    result = cursor.fetchone()
    conn.close()
    return result['total_revenue'] if result['total_revenue'] is not None else 0

def get_top_products(limit=3):
    conn = sqlite3.connect('chocolate.db')
    cursor = conn.cursor()
    query = '''
    SELECT p.id, p.name, SUM(oi.quantity) as total_sold
    FROM order_items oi
    JOIN products p ON oi.product_id = p.id
    JOIN orders o ON oi.order_id = o.id
    WHERE o.status IN ('paid', 'shipped', 'completed')
    GROUP BY p.id, p.name
    ORDER BY total_sold DESC
    LIMIT 
    '''
    cursor.execute(query, (limit,))
    results = cursor.fetchall()
    conn.close()
    return results

def get_coupon_usage():
    conn = sqlite3.connect('chocolate.db')
    cursor = conn.cursor()
    query = '''
    SELECT c.code, COUNT(o.id) as usage_count
    FROM coupons c
    LEFT JOIN orders o ON c.id = o.coupon_id
    GROUP BY c.id, c.code
    ORDER BY usage_count DESC
    '''
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

def discount_perfomance():
    conn = sqlite3.connect('chocolate.db')
    cursor = conn.cursor()
    
    results = cursor.fetchall()
    return results

print(run())