from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Company(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    company_name = db.Column(db.String(100))
    registration_number = db.Column(db.String(100))

    contact_person = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(50))


class Document(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    company_id = db.Column(
        db.Integer,
        db.ForeignKey('company.id')
    )

    document_name = db.Column(db.String(100))

    issue_date = db.Column(db.Date)

    expiry_date = db.Column(db.Date)

    status = db.Column(db.String(50))