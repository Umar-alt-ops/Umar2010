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
id INTEGER PRIMARY KEY AUTOINCREMENT,
title TEXT,
author_id INTEGER,
year INTEGER,
available BOOLEAN
)
''')

conn.commit()

cursor.execute('''
CREATE TABLE IF NOT EXISTS readers (
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
phone — TEXT
)
''')

conn.commit()

cursor.execute('''
CREATE TABLE IF NOT EXISTS borrows (
id INTEGER PRIMARY KEY AUTOINCREMENT,
book_id INTEGER,
reader_id INTEGER,
date_borrowed TEXT,
date_due TEXT,
returned BOOLEAN
)
''')    
conn.commit()

def authors(name, country):
    cursor.execute("INSERT INTO authors (name, country) VALUES (?, ?)", (name, country))
def books(title, author_id, year, avilable):
    cursor.execute("INSERT INTO books (title, author_id, year, available) VALUES (?, ?, ?, ?)", (title, author_id, year, avilable)
               ('1984', 1, 1949, True)) 
conn.commit()
print('Книга добавлена')