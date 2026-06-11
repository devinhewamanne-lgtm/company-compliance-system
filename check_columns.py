import sqlite3

conn = sqlite3.connect('company.db')
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(companies)")

columns = cursor.fetchall()

print("Columns in companies table:")

for column in columns:
    print(column)

conn.close()