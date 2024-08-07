# models.py

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class NaploBejegyzes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    datum = db.Column(db.String(10), nullable=False)
    cim = db.Column(db.String(100), nullable=False)
    tartalom = db.Column(db.Text, nullable=False)
