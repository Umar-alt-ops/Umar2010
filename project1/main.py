# import datetime
# print(datetime.datetime.now())
# import math
# print(math.sqrt(25))
# from project1.greetings import say_hello
# print(say_hello("World"))
# from tools.calc import multiply
# print(multiply(3, 4))

# import random
# for i in range(5):
#     print(random.randint(1, 100))

# import json
# nameage = {'name': 'Ivan', 'age': 24}
# text = json.dumps(nameage, ensure_ascii=False)
# print(text)

# import os
# print(os.getcwd())

import sqlite3

conn = sqlite3.connect('library.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS authors (
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
country TEXT
)
''')
conn.commit()

cursor.execute('''
CREATE TABLE IF NOT EXISTS books (
ids INTEGER PRIMARY KEY AUTOINCREMENT,
title TEXT,
author_id INTEGER PRIMARY KEY AUTOINCREMENT,
year INTEGER,
available BOOLEAN 
)
''')
conn.commit()