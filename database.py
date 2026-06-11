import sqlite3

# Create database connection
conn = sqlite3.connect("company.db")

cursor = conn.cursor()

# Company Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS companies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name TEXT NOT NULL,
    registration_number TEXT,
    address TEXT,
    contact_person TEXT,
    phone TEXT,
    email TEXT
)
""")

# Documents Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER,
    document_name TEXT,
    issue_date TEXT,
    expiry_date TEXT,
    reminder_days INTEGER,
    FOREIGN KEY(company_id) REFERENCES companies(id)
)
""")

conn.commit()
conn.close()

print("Database Created Successfully!")