from flask import Flask, render_template, request, redirect
from datetime import datetime, timedelta

import sqlite3

app = Flask(__name__)

# Home Page
@app.route('/')
def home():
    return render_template('index.html')


# Add Company
@app.route('/add-company', methods=['GET', 'POST'])
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
        conn.close()

        return redirect('/')

    return render_template('add_company.html')


# Add Document
@app.route('/add-document', methods=['GET', 'POST'])
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
        conn.close()

        return redirect('/')

    return render_template('add_document.html')

@app.route('/dashboard')
def dashboard():

    conn = sqlite3.connect('company.db')
    conn.row_factory = sqlite3.Row

    companies = conn.execute(
        "SELECT COUNT(*) AS total FROM companies"
    ).fetchone()

    documents = conn.execute(
        "SELECT COUNT(*) AS total FROM documents"
    ).fetchone()

    conn.close()

    return render_template(
        'dashboard.html',
        company_count=companies['total'],
        document_count=documents['total']
    )

@app.route('/expiring')
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

@app.route('/companies')
def company_list():

    search = request.args.get('search', '')

    conn = sqlite3.connect('company.db')
    cursor = conn.cursor()

    if search:
        cursor.execute("""
            SELECT * FROM companies
            WHERE company_name LIKE ?
            OR registration_number LIKE ?
            OR contact_person LIKE ?
        """,
        (
            f'%{search}%',
            f'%{search}%',
            f'%{search}%'
        ))
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

    conn = sqlite3.connect('company.db')
    conn.row_factory = sqlite3.Row

    company = conn.execute(
        "SELECT * FROM companies WHERE id=?",
        (id,)
    ).fetchone()

    if request.method == 'POST':

        company_name = request.form['company_name']
        registration_number = request.form['registration_no']
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
        conn.close()

        return redirect('/companies')

    conn.close()

    return render_template(
        'edit_company.html',
        company=company
    )

@app.route('/delete-company/<int:id>')
def delete_company(id):

    conn = sqlite3.connect('company.db')

    conn.execute(
        "DELETE FROM companies WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect('/companies')


if __name__ == '__main__':
    app.run(debug=True, port=3000)