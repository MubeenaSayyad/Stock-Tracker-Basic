import sqlite3

conn = sqlite3.connect("database.db")

conn.execute('''
CREATE TABLE IF NOT EXISTS users(
id INTEGER PRIMARY KEY AUTOINCREMENT,
email TEXT,
password TEXT,
balance REAL DEFAULT 10000
)
''')

conn.commit()
conn.close()

print("Database created successfully")