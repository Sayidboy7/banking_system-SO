from flask import Flask, abort, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from Bank.models import Bank, User, Type, FormatMoney, BankAccount, db
from flask_migrate import Migrate
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

# App configuration
app = Flask(__name__)
app.config['SECRET_KEY'] = 'sha:256df$joisdjf^jsdmsldpask&dpkpodksdlsdfsdpkfps'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bank.db'  #'postgresql://postgres:12345@localhost/bank_db'  
app.config['UPLOAD_FOLDER'] = 'Bank/static/images'
db.init_app(app=app)

# Login configuration
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Migrate
migrate = Migrate(app, db)


# Admin
class MyAdminIndexView(AdminIndexView):
	def is_accessinible(self):
		return current_user.is_authenticated and current_user.is_staff

	def inaccessible_callback(self, name, **kwargs):
		abort(404)


class SecureModelView(ModelView):
	def is_accessible(self):
		return current_user.is_authenticated and current_user.is_staff

	def inaccessible_callback(self, name, **kwargs):
		abort(404)


admin = Admin(app, template_mode='bootstrap4', index_view=MyAdminIndexView())

admin.add_view(SecureModelView(User, db.session))
admin.add_view(SecureModelView(Bank, db.session))
admin.add_view(SecureModelView(BankAccount, db.session))


@login_manager.user_loader
def load_user(id):
	return User.query.get(int(id))