'''База данных'''
'''
База данных - это упорядоченный набор структурированной информации или данных,которые обычно хранятся
в электронном виде в компьютерной системе.
База данных обычно управляется системой управления базами данных (СУБД).
Система управления базами данных - это комбинация, состоящая из языковых и программных средств,
которая осуществляет запись данных, доступ к ним, позволяет менять и удалять их, обеспечивает безопасность
и целостность данных.
* СУБД - это система, позволяющая создавать базы данных и манипулировать записями, 
хранящимися в них. А доступ к данным 'СУБД' осуществляется через специальный язык *SQL* *
SQL (Structured Query Language) - это язык структурированных запросов, основной задачей которого является предоставление 
способа считывания, записи, изменения и удаления информации в\из базы данных.
Вместе, данные и СУБД, а также связанные с ними приложения образуют систему базы данных.
Часто базы данных связаны с веб-сайтами и приложениями для хранения информации о пользователях,
продуктах, транзакциях и многом другом.
Базы данных могут быть реляционными (использующими таблицы для хранения данных) или нереляционными
(использующими различные структуры данных, такие как документы, графы или ключ-значение).
'''
import sqlite3
# Подключаемся (или создаем, если файла нет) database
conn = sqlite3.connect('school.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    age INTEGER,
    email TEXT
)
''')
conn.commit()  # Сохраняем изменения
''''CRUD - Create, Read, Update, Delete'''
# cursor.execute("INSERT INTO students (name, age, email) VALUES (?, ?, ?)", 
#                 ('Азамат', 14, 
#             "azamat@example.com"))
# # conn.commit()
# cursor.execute("INSERT INTO students (name, age, email) VALUES (?, ?, ?)", 
#                 ('Малика', 16, 
#             "malika@example.com"))
# conn.commit()
# cursor.execute("INSERT INTO students (name, age, email) VALUES (?, ?, ?)", 
#                 ('Медина', 17, 
#             "medina@example.com"))
# conn.commit()
# ------READ (чтение данных)------ 
# print("\n ====== Все студенты ======")
# cursor.execute("SELECT * FROM students")
# for row in cursor.fetchall():
#     print(row)
# ------ (обновление данных)------
# cursor.execute("SELECT name FROM students")
# print("\n ====== Имена студентов ======")
# for row in cursor.fetchall():
#     print(row[0])

# # ------UPDATE (обновление данных)------
# cursor.execute("UPDATE students SET age = 18 WHERE name = 'Малика'")
# conn.commit()
# print("\n ====== Обновление данных ======")
# cursor.execute("SELECT * FROM students")
# for row in cursor.fetchall():
#     print(row)
# ------DELETE (удаление данных)------
# cursor.execute("DELETE FROM students WHERE name = 'Азамат'")
# conn.commit()
# print("\n ====== После удаления ======")
# cursor.execute("SELECT * FROM students")
# for row in cursor.fetchall():
#     print(row)
# # Закрываем соединение
# conn.close()
