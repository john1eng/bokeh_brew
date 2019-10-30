
from flask_sqlalchemy import SQLAlchemy
from main import app
import os

DATABASE_URL = 'postgresql+psycopg2://postgres:password@localhost:5432/brewasis'
app.config['SQLALCHEMY_DATABASE_URI']=DATABASE_URL


db = SQLAlchemy(app)

class Login(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    users = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(30), nullable=False)

    def __init__(self, users, password):
        self.users = users
        self.password = password

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return '<users = %r, password = %r>' % (self.users, self.password)
