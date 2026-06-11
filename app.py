from flask import Flask, render_template, request, redirect, url_for,session
import sqlite3
from datetime import date, timedelta, datetime
from apscheduler.schedulers.background import BackgroundScheduler

import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta

import csv
from io import BytesIO
from flask import send_file
import openpyxl

from flask import Response
from io import StringIO

from flask import session
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

from reportlab.platypus import SimpleDocTemplate, Table
from reportlab.platypus import TableStyle
from reportlab.lib import colors

import openpyxl

from reportlab.platypus import SimpleDocTemplate, Table
from reportlab.platypus import TableStyle
from reportlab.lib import colors




EMAIL_ADDRESS = "companyreminder@gmail.com"
EMAIL_PASSWORD = "rvsm xdnz kfgb fxzx"

def send_email(recipient, subject, body):

    msg = MIMEText(body)

    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = recipient

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(
            EMAIL_ADDRESS,
            EMAIL_PASSWORD
        )

        server.send_message(msg)


app = Flask(__name__)

def log_action(user_id, action):

    conn = sqlite3.connect('company.db')

    conn.execute(
        """
        INSERT INTO audit_logs
        (user_id, action)
        VALUES (?, ?)
        """,
        (user_id, action)
    )

    conn.commit()
    conn.close()

def admin_required():

    if session.get('role') != 'admin':
        return False

    return True


from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        if 'user_id' not in session:
            return redirect('/login')

        return f(*args, **kwargs)

    return decorated_function    

app.secret_key = 'mysecretkey123'

def create_users_table():
    conn = sqlite3.connect('company.db')

    conn.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT DEFAULT 'staff'
    )
    """)

    conn.commit()
    conn.close()


def create_admin_user():

    conn = sqlite3.connect('company.db')

    existing = conn.execute(
        "SELECT * FROM users WHERE username=?",
        ("admin",)
    ).fetchone()

    if not existing:

        conn.execute("""
        INSERT INTO users
        (username,password,role)
        VALUES (?,?,?)
        """, (
            "admin",
            generate_password_hash("admin123"),
            "admin"
        ))

        conn.commit()

    conn.close()


def get_renewal_notifications():

    conn = sqlite3.connect('company.db')
    conn.row_factory = sqlite3.Row

    documents = conn.execute("""
        SELECT
            documents.*,
            companies.company_name
        FROM documents
        LEFT JOIN companies
        ON documents.company_id = companies.id
        ORDER BY documents.expiry_date
    """).fetchall()

    conn.close()

    notifications = []

    today = datetime.today().date()

    for doc in documents:

        expiry_date = datetime.strptime(
            doc['expiry_date'],
            '%Y-%m-%d'
        ).date()

        days_left = (expiry_date - today).days

        if days_left in [30, 15, 7, 1]:

            notifications.append({
                'company_name': doc['company_name'],
                'document_name': doc['document_name'],
                'expiry_date': doc['expiry_date'],
                'days_left': days_left
            })

    return notifications

def get_renewal_alerts():

    conn = sqlite3.connect('company.db')
    conn.row_factory = sqlite3.Row

    documents = conn.execute("""
        SELECT
            documents.*,
            companies.company_name
        FROM documents
        LEFT JOIN companies
        ON documents.company_id = companies.id
    """).fetchall()

    conn.close()

    alerts = []

    today = date.today()

    for doc in documents:

        if doc['expiry_date']:

            expiry = datetime.strptime(
                doc['expiry_date'],
                '%Y-%m-%d'
            ).date()

            days_left = (expiry - today).days

            if days_left in [30, 15, 7, 1]:

                alerts.append({
                    'company_name': doc['company_name'],
                    'document_name': doc['document_name'],
                    'expiry_date': doc['expiry_date'],
                    'days_left': days_left
                })

    return alerts




    conn = sqlite3.connect('company.db')
    conn.row_factory = sqlite3.Row

    documents = conn.execute("""
        SELECT
            documents.*,
            companies.company_name
        FROM documents
        LEFT JOIN companies
        ON documents.company_id = companies.id
    """).fetchall()

    conn.close()

    alerts = []

    today = date.today()

    for doc in documents:

        if doc['expiry_date']:

            expiry = datetime.strptime(
                doc['expiry_date'],
                '%Y-%m-%d'
            ).date()

            days_left = (expiry - today).days

            if days_left in [30, 15, 7, 1]:

                alerts.append({
                    'company_name': doc['company_name'],
                    'document_name': doc['document_name'],
                    'expiry_date': doc['expiry_date'],
                    'days_left': days_left
                })

    return alerts

@app.route('/users', methods=['GET', 'POST'])
def users():

    if not admin_required():
        return "Access Denied"

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        conn = sqlite3.connect('company.db')

        conn.execute("""
            INSERT INTO users
            (username,password,role)
            VALUES (?,?,?)
        """, (
            username,
            generate_password_hash(password),
            role
        ))

        conn.commit()
        conn.close()

        return redirect('/users')

    return render_template('users.html')

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if not admin_required():
        return "Access Denied"
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        
        
        try:
            conn = sqlite3.connect('company.db')
            conn.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                (username, generate_password_hash(password), role)
            )
            conn.commit()
            return "User added successfully"
        finally:
            conn.close()
    
    return '''
        <form method="POST">
            <input name="username" placeholder="Username">
            <input name="password" placeholder="Password" type="password">
            <button type="submit">Add User</button>
        </form>
    '''

def create_admin_user():
    conn = sqlite3.connect('company.db')
    try:
        existing = conn.execute(
            "SELECT * FROM users WHERE username = ?",
            ("admin",)
        ).fetchone()
 
        if not existing:
            conn.execute("""
                INSERT INTO users (username, password, role)
                VALUES (?, ?, ?)
            """, (
                "admin",
                generate_password_hash("admin123"),
                "admin"
            ))
            conn.commit()
            print("Admin user created successfully")
        else:
            # Auto-fix if password is still plain text
            if existing[2] == "admin123":
                conn.execute(
                    "UPDATE users SET password=? WHERE username=?",
                    (generate_password_hash("admin123"), "admin")
                )
                conn.commit()
                print("Admin password fixed: now hashed")
            else:
                print("Admin user already exists with hashed password")
    finally:
        conn.close()


@app.route('/delete_user/<int:id>')
def delete_user(id):
    if not admin_required():
        return "Access Denied"
    
    try:
        conn = sqlite3.connect('company.db')
        conn.execute("DELETE FROM users WHERE id = ?", (id,))
        conn.commit()
        return "User deleted successfully"
    finally:
        conn.close()


# Home Page
@app.route('/')
def home():

    if 'user_id' not in session:
        return redirect('/login')

    alerts = get_renewal_alerts()

    conn = sqlite3.connect('company.db')
    conn.row_factory = sqlite3.Row

    total_companies = conn.execute(
        "SELECT COUNT(*) FROM companies"
    ).fetchone()[0]

    documents = conn.execute(
        "SELECT * FROM documents"
    ).fetchall()

    conn.close()

    today = datetime.today().date()

    expired_count = 0
    expiring_count = 0

    for doc in documents:

        expiry_date = datetime.strptime(
            doc['expiry_date'],
            '%Y-%m-%d'
        ).date()

        days_left = (expiry_date - today).days

        if days_left < 0:
            expired_count += 1

        elif days_left <= 30:
            expiring_count += 1

    

    return render_template(
        'index.html',
      
    )

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('company.db')
        conn.row_factory = sqlite3.Row

        user = conn.execute(
            "SELECT * FROM users WHERE username=?",
            (username,)
        ).fetchone()

        conn.close()

        if user and check_password_hash(
            user['password'],
            password
        ):
            session['user_id'] = user['id']
            session['role'] = user['role']
            session['username'] = user['username']
        
        log_action(
        user['id'],
            f"Logged in as {user['username']}"
)
        return redirect('/')

        return "Invalid username or password"

    return render_template('login.html')

# Add Company
@app.route('/add-company', methods=['GET', 'POST'])
@login_required
def add_company():

    if request.method == 'POST':

        company_name = request.form['company_name']
        registration_number = request.form['registration_number']
        address = request.form['address']
        contact_person = request.form['contact_person']
        phone = request.form['phone']
        email = request.form['email']

        conn = sqlite3.connect('company.db')
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO companies
        (company_name, registration_number, address,
         contact_person, phone, email)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            company_name,
            registration_number,
            address,
            contact_person,
            phone,
            email
        ))

        conn.commit()

        log_action(
        session['user_id'],
        f"Added company: {company_name}"
        )
        conn.close()

        return redirect('/')

    return render_template('add_company.html')


@app.route('/documents')
@login_required
def documents():

    conn = sqlite3.connect('company.db')
    conn.row_factory = sqlite3.Row

    documents = conn.execute("""
        SELECT
            documents.*,
            companies.company_name
        FROM documents
        LEFT JOIN companies
        ON documents.company_id = companies.id
        ORDER BY documents.expiry_date
    """).fetchall()

    conn.close()

    today = datetime.today().date()

    processed_documents = []

    for doc in documents:

        expiry = datetime.strptime(
            doc['expiry_date'],
            '%Y-%m-%d'
        ).date()

        days_left = (expiry - today).days

        if days_left < 0:
            status = "Expired"
            priority = 1

        elif days_left <= 30:
            status = "Expiring Soon"
            priority = 2

        else:
            status = "Active"
            priority = 3

        processed_documents.append({
            'id': doc['id'],
            'company_name': doc['company_name'],
            'document_name': doc['document_name'],
            'expiry_date': doc['expiry_date'],
            'status': status,
            'days_left': days_left,
            'priority': priority
        })

    processed_documents.sort(
        key=lambda x: (
            x['priority'],
            x['days_left']
        )
    )

    return render_template(
        'documents.html',
        documents=processed_documents
    )

@app.route('/edit-document/<int:id>', methods=['GET', 'POST'])
def edit_document(id):

    if not admin_required():
        return "Access Denied"

    conn = sqlite3.connect('company.db')
    conn.row_factory = sqlite3.Row

    document = conn.execute(
        "SELECT * FROM documents WHERE id=?",
        (id,)
    ).fetchone()

    if request.method == 'POST':

        document_name = request.form['document_name']
        issue_date = request.form['issue_date']
        expiry_date = request.form['expiry_date']
        reminder_days = request.form['reminder_days']

        conn.execute("""
            UPDATE documents
            SET document_name=?,
                issue_date=?,
                expiry_date=?,
                reminder_days=?
            WHERE id=?
        """,
        (
            document_name,
            issue_date,
            expiry_date,
            reminder_days,
            id
        ))

        conn.commit()

        log_action(
       session['user_id'],
        f"Edited document: {document_name}"
        )
        conn.close()

        return redirect('/documents')

    conn.close()

    return render_template(
        'edit_document.html',
        document=document
    )

@app.route('/delete-document/<int:id>')
def delete_document(id):

    if not admin_required():
        return "Access Denied"

    conn = sqlite3.connect('company.db')

    conn.execute(
        "DELETE FROM documents WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    log_action(
    session['user_id'],
    f"Deleted document ID {id}"
)

    return redirect('/documents')

@app.route('/view-document/<int:id>')
def view_document(id):

    conn = sqlite3.connect('company.db')
    conn.row_factory = sqlite3.Row

    document = conn.execute(
        'SELECT * FROM documents WHERE id = ?',
        (id,)
    ).fetchone()

    conn.close()

    return render_template(
        'view_document.html',
        document=document
    )


def send_renewal_reminders():
    documents = check_expiring_documents()

    for doc in documents:
        subject = (
            f"Renewal Reminder - "
            f"{doc['document_name']}"
        )

        body = f"""
Company:
{doc['company_name']}

Document:
{doc['document_name']}

Expiry Date:
{doc['expiry_date']}

Please renew before expiry.
"""

        send_email(
            doc['email'],
            subject,
            body
        )


@app.route('/test-email')
def test_email():

    send_renewal_reminders()

    return "Emails Sent"



# Add Document
@app.route('/add-document', methods=['GET', 'POST'])
@login_required
def add_document():

    if request.method == 'POST':

        company_id = request.form['company_id']
        document_name = request.form['document_name']
        issue_date = request.form['issue_date']
        expiry_date = request.form['expiry_date']
        reminder_days = request.form['reminder_days']

        conn = sqlite3.connect('company.db')
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO documents
        (company_id, document_name,
         issue_date, expiry_date,
         reminder_days)
        VALUES (?, ?, ?, ?, ?)
        """, (
            company_id,
            document_name,
            issue_date,
            expiry_date,
            reminder_days
        ))

        conn.commit()

        log_action(
       session['user_id'],
        f"Added document: {document_name}"
    )
        conn.close()

        return redirect('/')

    return render_template('add_document.html')

@app.route('/dashboard')
@login_required
def dashboard():

    conn = sqlite3.connect('company.db')
    conn.row_factory = sqlite3.Row

    total_companies = conn.execute(
        "SELECT COUNT(*) FROM companies"
    ).fetchone()[0]

    documents = conn.execute(
        "SELECT * FROM documents"
    ).fetchall()

    conn.close()

    alerts = get_renewal_alerts()

    today = datetime.today().date()

    expired_count = 0
    expiring_count = 0

    for doc in documents:

        expiry_date = datetime.strptime(
            doc['expiry_date'],
            '%Y-%m-%d'
        ).date()

        days_left = (expiry_date - today).days

        if days_left < 0:
            expired_count += 1

        elif days_left <= 30:
            expiring_count += 1

    return render_template(
        'dashboard.html',
        alerts=alerts,
        total_companies=total_companies,
        total_documents=len(documents),
        expired_count=expired_count,
        expiring_count=expiring_count
    )
@app.route('/expiring')
@login_required
def expiring():

    today = datetime.today().date()

    conn = sqlite3.connect('company.db')
    conn.row_factory = sqlite3.Row

    docs = conn.execute("""
        SELECT *
        FROM documents
        WHERE expiry_date >= ?
        ORDER BY expiry_date
    """, (today,)).fetchall()

    conn.close()

    return render_template(
        'expiring.html',
        documents=docs
    )


@app.route('/alerts/30')
def alert_30():

    target = datetime.today().date() + timedelta(days=30)

    conn = sqlite3.connect('company.db')
    conn.row_factory = sqlite3.Row

    docs = conn.execute("""
        SELECT *
        FROM documents
        WHERE expiry_date <= ?
    """, (target,)).fetchall()

    conn.close()

    return render_template(
        'alerts.html',
        documents=docs,
        title="30 Day Alerts"
    )



@app.route('/alerts/15')
def alert_15():

    target = datetime.today().date() + timedelta(days=15)

    conn = sqlite3.connect('company.db')
    conn.row_factory = sqlite3.Row

    docs = conn.execute("""
        SELECT *
        FROM documents
        WHERE expiry_date <= ?
    """, (target,)).fetchall()

    conn.close()

    return render_template(
        'alerts.html',
        documents=docs,
        title="15 Day Alerts"
    )


@app.route('/alerts/7')
def alert_7():

    target = datetime.today().date() + timedelta(days=7)

    conn = sqlite3.connect('company.db')
    conn.row_factory = sqlite3.Row

    docs = conn.execute("""
        SELECT *
        FROM documents
        WHERE expiry_date <= ?
    """, (target,)).fetchall()

    conn.close()

    return render_template(
        'alerts.html',
        documents=docs,
        title="7 Day Alerts"
    )

@app.route('/alerts')
@login_required
def all_alerts():

    today = datetime.today().date()

    conn = sqlite3.connect('company.db')
    conn.row_factory = sqlite3.Row

    documents = conn.execute("""
        SELECT
            documents.*,
            companies.company_name
        FROM documents
        LEFT JOIN companies
        ON documents.company_id = companies.id
        ORDER BY documents.expiry_date
    """).fetchall()

    conn.close()

    alerts = []

    for doc in documents:

        expiry_date = datetime.strptime(
            doc['expiry_date'],
            '%Y-%m-%d'
        ).date()

        days_left = (expiry_date - today).days

        if days_left <= 30:

            status = "Active"

            if days_left < 0:
                status = "Expired"
            elif days_left <= 7:
                status = "Expiring Soon"

            priority = 3

            if status == "Expired":
                priority = 1
            elif status == "Expiring Soon":
                priority = 2

            alerts.append({
                'company_name': doc['company_name'],
                'document_name': doc['document_name'],
                'expiry_date': doc['expiry_date'],
                'days_left': days_left,
                'status': status,
                'priority': priority
            })

    alerts.sort(
        key=lambda x: (
            x['priority'],
            x['days_left']
        )
    )

    return render_template(
        'all_alerts.html',
        alerts=alerts
    )

@app.route('/companies')
@login_required
def company_list():

    if 'user_id' not in session:
        return redirect('/login')

    search = request.args.get('search')

    conn = sqlite3.connect('company.db')
    cursor = conn.cursor()

    if search:

        cursor.execute(
            """
            SELECT *
            FROM companies
            WHERE company_name LIKE ?
            OR registration_number LIKE ?
            """,
            (
                '%' + search + '%',
                '%' + search + '%'
            )
        )

    else:

        cursor.execute(
            "SELECT * FROM companies"
        )

    companies = cursor.fetchall()

    conn.close()

    return render_template(
        'company_list.html',
        companies=companies
    )


@app.route('/edit-company/<int:id>', methods=['GET', 'POST'])
def edit_company(id):

    if not admin_required():
        return "Access Denied"

    conn = sqlite3.connect('company.db')
    conn.row_factory = sqlite3.Row

    company = conn.execute(
        "SELECT * FROM companies WHERE id=?",
        (id,)
    ).fetchone()

    if request.method == 'POST':

        company_name = request.form['company_name']
        registration_number = request.form['registration_number']
        contact_person = request.form['contact_person']
        email = request.form['email']
        phone = request.form['phone']

        conn.execute("""
            UPDATE companies
            SET company_name=?,
                registration_number=?,
                contact_person=?,
                email=?,
                phone=?
            WHERE id=?
        """,
        (
            company_name,
            registration_number,
            contact_person,
            email,
            phone,
            id
        ))

        conn.commit()

        log_action(
        session['user_id'],
        f"Edited company: {company_name}"
    )
        conn.close()

        return redirect('/companies')

    conn.close()

    return render_template(
        'edit_company.html',
        company=company
    )

@app.route('/delete-company/<int:id>')
def delete_company(id):

    if not admin_required():
        return "Access Denied"

    conn = sqlite3.connect('company.db')
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM companies WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    log_action(
    session['user_id'],
    f"Deleted company ID {id}"
)

    return redirect('/companies')

def check_expiring_documents():
    conn = sqlite3.connect('company.db')
    conn.row_factory = sqlite3.Row

    today = datetime.today().date()
    target_date = today + timedelta(days=30)

    documents = conn.execute("""
        SELECT
            documents.*,
            companies.email,
            companies.company_name
        FROM documents
        JOIN companies
        ON documents.company_id = companies.id
        WHERE expiry_date <= ?
    """, (target_date,)).fetchall()

    conn.close()
    return documents


scheduler = BackgroundScheduler()

scheduler.add_job(
    send_renewal_reminders,
    'cron',
    hour=8,
    minute=0
)

scheduler.start()

@app.route('/export_companies_csv')
def export_companies_csv():

    conn = sqlite3.connect('company.db')
    conn.row_factory = sqlite3.Row

    companies = conn.execute("""
        SELECT *
        FROM companies
    """).fetchall()

    conn.close()

    output = StringIO()

    writer = csv.writer(output)

    writer.writerow([
        'ID',
        'Company Name',
        'Registration Number',
        'Email',
        'Phone'
    ])

    for company in companies:
        writer.writerow([
            company['id'],
            company['company_name'],
            company['registration_number'],
            company['email'],
            company['phone']
        ])

    output.seek(0)

    return Response(
        output,
        mimetype="text/csv",
        headers={
            "Content-Disposition":
            "attachment; filename=companies.csv"
        }
    )

@app.route('/export_companies_pdf')
def export_companies_pdf():

    conn = sqlite3.connect('company.db')
    conn.row_factory = sqlite3.Row

    companies = conn.execute("""
        SELECT *
        FROM companies
    """).fetchall()

    conn.close()

    pdf_buffer = BytesIO()

    doc = SimpleDocTemplate(pdf_buffer)

    data = [
        [
            "ID",
            "Company Name",
            "Registration Number",
            "Email",
            "Phone"
        ]
    ]

    for company in companies:
        data.append([
            company['id'],
            company['company_name'],
            company['registration_number'],
            company['email'],
            company['phone']
        ])

    table = Table(data)

    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('GRID', (0,0), (-1,-1), 1, colors.black)
    ]))

    elements = [table]

    doc.build(elements)

    pdf_buffer.seek(0)

    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name="companies_report.pdf",
        mimetype="application/pdf"
    )

conn = sqlite3.connect('company.db')



@app.route('/logout')
def logout():

    session.clear()

    return redirect('/login')

@app.route('/export_companies_excel')
def export_companies_excel():

    conn = sqlite3.connect('company.db')
    conn.row_factory = sqlite3.Row

    companies = conn.execute("""
        SELECT *
        FROM companies
    """).fetchall()

    conn.close()

    workbook = openpyxl.Workbook()
    sheet = workbook.active

    sheet.title = "Companies"

    headers = [
        "ID",
        "Company Name",
        "Registration Number",
        "Email",
        "Phone"
    ]

    sheet.append(headers)

    for company in companies:
        sheet.append([
            company['id'],
            company['company_name'],
            company['registration_number'],
            company['email'],
            company['phone']
        ])

    output = BytesIO()
    workbook.save(output)
    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name="companies.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


conn = sqlite3.connect('company.db')

try:
    conn.execute("""
    ALTER TABLE users
    ADD COLUMN role TEXT DEFAULT 'staff'
    """)
    conn.commit()

except:
    pass

conn.close()


@app.route('/audit-logs')
def audit_logs():

    if not admin_required():
        return "Access Denied"

    conn = sqlite3.connect('company.db')
    conn.row_factory = sqlite3.Row

    logs = conn.execute("""
        SELECT *
        FROM audit_logs
        ORDER BY timestamp DESC
    """).fetchall()

    conn.close()

    return render_template(
        'audit_logs.html',
        logs=logs
    )

if __name__ == '__main__':
    create_users_table()
    create_admin_user()
    app.run(port=3000)
    