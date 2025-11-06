import sqlite3

# === Создание и подключение к базе данных ===
conn = sqlite3.connect("bank.db")
cursor = conn.cursor()

# === Создание таблиц ===
cursor.execute("""
CREATE TABLE IF NOT EXISTS clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    balance INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_name TEXT,
    amount INTEGER,
    type TEXT  -- 'deposit' или 'withdraw'
)
""")
conn.commit()

# === Добавляем клиентов ===

cursor.execute("INSERT INTO clients (name, balance) VALUES (?, ?)", 
            ('Али', 10000))

conn.commit()

cursor.execute("INSERT INTO clients (name, balance) VALUES (?, ?)",
               ('Малика', 5000))

conn.commit()

cursor.execute("INSERT INTO clients (name, balance) VALUES (?, ?)",
               ('Тимур', 7000))

conn.commit()

print("\n--- Клиенты до перевода ---")
for row in cursor.execute("SELECT * FROM clients"):
    print(row)

# Перевод: Малика -> Али 2000

# Уменьшаем баланс Малики
cursor.execute("UPDATE clients SET balance = balance - 2000 WHERE name = 'Малика'")
conn.commit()

# Увеличиваем баланс Али
cursor.execute("UPDATE clients SET balance = balance + 2000 WHERE name = 'Али'")

conn.commit()

# === Добавляем транзакции ===
cursor.execute("INSERT INTO transactions (client_name, amount, type) VALUES (?, ?, ?)",
            ("Малика", 2000, "withdraw"))
            
cursor.execute("INSERT INTO transactions (client_name, amount, type) VALUES (?, ?, ?)",
            ("Али", 2000, "deposit"))

conn.commit()

print("\n--- Таблица транзакций ---")
for row in cursor.execute("SELECT * FROM transactions"):
    print(row)

# === Удаляем клиентов с балансом < 6000 ===
# cursor.execute("DELETE FROM clients WHERE balance < 6000")
# conn.commit()

print("\n--- Клиенты после удаления ---")
for row in cursor.execute("SELECT * FROM clients"):
    print(row)

# === Закрываем соединение ===
conn.close()
print("\nБаза данных 'bank.db' успешно создана и сохранена!")