from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin
import random

db = SQLAlchemy()

# Spacial function for generate a random account number
def random_digit():
	""" Function for generate a unique account number """
	result = ''
	for i in range(12):
		result += str(random.randint(0, 9))

	result = int(result)
	return result


# Models
class Bank(db.Model):
	__tablename__ = 'banks'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(255), nullable=False)

	bank_accounts = db.relationship('BankAccount', backref='bank')

	def __repr__(self):
		return f'{self.id} : {self.name}'


class User(db.Model, UserMixin):
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(255), nullable=False, unique=True)
	full_name = db.Column(db.String(300))
	bio = db.Column(db.String(255))
	password = db.Column(db.String(), nullable=False)
	is_staff = db.Column(db.Boolean)

	bank_accounts = db.relationship('BankAccount', backref='user')

	def __repr__(self):
		return self.username


class BankAccount(db.Model):
	__tablename__ = 'bankaccounts'
	id = db.Column(db.Integer, primary_key=True)
	login_name = db.Column(db.String(255), nullable=False, unique=True)
	full_name = db.Column(db.String(255))
	code = db.Column(db.Integer, nullable=False)
	account_number = db.Column(db.Integer, default=random_digit())
	comment = db.Column(db.String(120), default='')
	balance = db.Column(db.Integer, default=0)
	status = db.Column(db.String(), default='active')
	user_id = db.Column(db.Integer, db.ForeignKey(User.id))
	bank_id = db.Column(db.Integer, db.ForeignKey(Bank.id))

	created_at = db.Column(db.DateTime(), default=datetime.now)

	def __repr__(self):
		return f'{self.id} : {self.user} & {self.login_name}-bank:{self.bank}'
