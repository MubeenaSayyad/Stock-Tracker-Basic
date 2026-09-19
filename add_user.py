import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute(
"INSERT INTO users (email,password,balance) VALUES (?,?,?)",
("test@gmail.com","1234",10000)
)

conn.commit()
conn.close()

print("User added successfully")