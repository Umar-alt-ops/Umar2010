# import sqlite3
# conn = sqlite3.connect('company.db')
# cursor = conn.cursor()
# cursor.execute('''
# CREATE TABLE IF NOT EXISTS employees (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     name TEXT NOT NULL,
#     age INTEGER,
#     position TEXT
# )
# ''')
# conn.commit()
# cursor.execute("INSERT INTO employees (name, age, position) VALUES (?, ?, ?)", 
#                 ('Али', 25, 'Программист'))
# conn.commit()
# cursor.execute("INSERT INTO employees (name, age, position) VALUES (?, ?, ?)", 
#                 ('Айнура', 28, 'дизайнер'))
# conn.commit()
# cursor.execute("INSERT INTO employees (name, age, position) VALUES (?, ?, ?)", 
#                 ('Тимур', 22, 'тестировщик'))
# conn.commit()
# cursor.execute("SELECT name FROM employees")
# print("\n ====== Имена сотрудников ======")
# for row in cursor.fetchall():
#     print(row[0])
# cursor.execute("UPDATE employees SET age = 29 WHERE name = 'Айнура'")
# conn.commit()
# cursor.execute("SELECT * FROM employees")
# for row in cursor.fetchall():
#     print(row)
# cursor.execute("DELETE FROM employees WHERE name = 'Тимур'")
# conn.commit()
# print("\n ====== После удаления ======")
# cursor.execute("SELECT * FROM employees")
# for row in cursor.fetchall():
#     print(row)

# conn.close()
import sqlite3
conn = sqlite3.connect('school_v2.db')
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    age INTEGER,
    email TEXT, 
    grade INTEGER
)
''')
conn.commit()
cursor.execute("INSERT INTO students (name, age, email, grade) VALUES (?, ?, ?, ?)", 
                ('Айгуль', 15,
                'aigul@example.com', 9))
conn.commit()
# cursor.execute("INSERT INTO students (name, age, email, grade) VALUES (?, ?, ?, ?)", 
#                 ('Азамат', 16,
#                  'azamat@example.com', 10))
# conn.commit()
# cursor.execute("INSERT INTO students (name, age, email, grade) VALUES (?, ?, ?, ?)",
#                 ('Малика', 17,
#                  'malika@example.com', 11))
# conn.commit()
# cursor.execute("INSERT INTO students (name, age, email, grade) VALUES (?, ?, ?, ?)",
#                 ('Тимур', 16,
#                   'timur@example.com', 10))
# conn.commit()
# cursor.execute("INSERT INTO students (name, age, email, grade) VALUES (?, ?, ?, ?)",
#                 ('Алина', 15,
#                   'alina@example.com', 9))
# conn.commit()
print("\n ====== Все студенты ======")
cursor.execute("SELECT * FROM students")
for row in cursor.fetchall():
    print(row)
print("\n ====== Студенты 10 класса ======")
cursor.execute("SELECT * FROM students WHERE grade = 10")
for row in cursor.fetchall():
    print(row)
print("\n ====== Имена и почты всех студентов ======")
cursor.execute("SELECT name, email FROM students")
for row in cursor.fetchall():
    print(row)
cursor.execute("SELECT * FROM students WHERE age > 15")
print("\n ====== Студенты старше 15 лет ======")
for row in cursor.fetchall():
    print(row)
cursor.execute("UPDATE students SET grade = 10 WHERE name = 'Айгуль'")
cursor.execute("UPDATE students SET grade = 10 WHERE name = 'Алина'")
conn.commit()
print("\n ====== Обновление данных ======")
cursor.execute("SELECT * FROM students")
for row in cursor.fetchall():
    print(row)
cursor.execute("UPDATE students SET email = 'timur10@example.com' WHERE name = 'Тимур'")
conn.commit()
cursor.execute("UPDATE students SET age = age + 1")
conn.commit()
print("\n ====== После изменений ======")
cursor.execute("SELECT * FROM students")
for row in cursor.fetchall():
    print(row)
cursor.execute("DELETE FROM students WHERE age < 16")
conn.commit()
print("\n ====== После удаления ======")
cursor.execute("SELECT * FROM students")
for row in cursor.fetchall():
    print(row)
