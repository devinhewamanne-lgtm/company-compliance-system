import sqlite3

conn = sqlite3.connect("company.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM companies")

for row in cursor.fetchall():
    print(row)

conn.close()