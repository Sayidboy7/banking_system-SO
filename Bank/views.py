from Bank import *
import random
from datetime import datetime, timedelta

# Spacial function for generate a random account number
def random_digit():
    """ Function for generate a unique account number """
    result = ''
    for i in range(12):
        result += str(random.randint(0, 9))

    result = int(result)
    return result


# Views
@app.route('/')
def index():
    """ This is the main page of the entire banking system """
    banks = Bank.query.all()

    banks_list = [bank for bank in banks]

    return render_template('index.html', banks=banks)


@app.route('/bank/<string:bank_name>')
@login_required
def bank_home(bank_name):
    """ This is the SO bank page and shows the user a accounts registered on """
    bank = Bank.query.filter_by(name=bank_name).first()
    bank_accounts = BankAccount.query.filter_by(bank_id=bank.id, user_id=current_user.id).all()

    account = [account for account in bank_accounts]

    return render_template('accounts_bank.html', bank=bank, bank_accounts=bank_accounts)


@app.route('/register', methods=['POST', 'GET'])
def register():
    """ Registers the user to the system """
    if request.method == 'POST':
        username = request.form.get('username').strip()
        full_name = request.form.get('full_name').strip()
        password1 = request.form.get('password1').strip()
        password2 = request.form.get('password2').strip()

        check_username = User.query.filter(User.username == username).first()

        if check_username:
            flash('This username already registered!', category='warning')
            return redirect(url_for('register'))

        if not full_name or not username:
            flash('Please complete the form!', category='warning')
            return redirect(url_for('register'))

        if len(password1) < 4:
            flash('Password must be greater than 4!', category='error')
            return redirect(url_for('register'))

        if password1 != password2:
            flash('Passwords are must be equal!')
            return redirect(url_for('register'))

        user = User(
            username=username,
            full_name=full_name,
            password=generate_password_hash(password1)
        )

        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    """ This is the login fuction for user login the system and use it 100% """
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password').strip()

        check_user = User.query.filter_by(username=username).first()

        if check_user and check_password_hash(check_user.password, password):
            login_user(check_user)
            return redirect(url_for('index'))
        else:
            flash('Incorrect username or password!', category='error')
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/profile/<int:id>')
def profile(id):
    user = User.query.get_or_404(id)
    count_accounts = len(BankAccount.query.filter_by(user_id=user.id).all())


    return render_template('profile.html', user=user, count_accounts=count_accounts)


@app.route('/edit/profile/<int:id>', methods=['POST','GET'])
def edit_profile(id):
    user = User.query.get_or_404(id)
    if request.method == 'POST':
        username = request.form.get('username')
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        bio = request.form.get('bio')
        file = request.files['image']

        if not username or not full_name or not email:
            flash('User requeired information can\' be empty!')
            return redirect(url_for('edit_profile',id=id))

        if file.filename != '':
            image = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], image)

            file.save(file_path)

        else:
            image = user.photo


        user.username = username
        user.full_name = full_name
        user.email = email
        user.bio = bio
        user.photo = image

        db.session.commit()

        return redirect(url_for('profile', id=id))

    return render_template('edit_profile.html', user=user)


@app.route('/<string:bank_name>/register/bank-account/<string:type>', methods=['POST', 'GET'])
@login_required
def create_bank_account(bank_name, type):
    """ This is the create account or register can create a user and user bank account """
    bank = Bank.query.filter_by(name=bank_name).first()
    if request.method == 'POST':
        login_name = request.form.get('login_name').strip()
        comment = request.form.get('comment')
        code = request.form.get('code').strip()
        deposit = request.form.get('deposit')
        bank = Bank.query.filter_by(name=bank_name).first()
        format = request.form.get('format')

        check_login = BankAccount.query.filter_by(login_name=login_name).first()

        if not login_name or not comment or not code:
            flash('Please complete the form!', category='warning')
            return redirect(url_for('create_bank_account', bank_name=bank.name, type=type))

        if check_login:
            flash('This login name alredy busy please choose another', category='warning')
            return redirect(url_for('create_bank_account', bank_name=bank.name, type=type))

        if len(code) < 4:
            flash('The code must be longer than 4 or must be difficult!', category='warning')
            return redirect(url_for('create_bank_account', bank_name=bank_name, type=type))

        bank_account = BankAccount(
            login_name=login_name,
            full_name = current_user.full_name,
            code=code,
            account_number=random_digit(),
            type=type,
            comment=comment,
            format = format,
            bank_id=bank.id,
            bank_name=bank.name,
            user_id=current_user.id,
            balance=int(deposit) if deposit and int(deposit) <= 5 else 0
        )

        db.session.add(bank_account)
        db.session.commit()

        return redirect(url_for('bank_home', bank_name=bank_name))

    bank_accounts = BankAccount.query.filter_by(user_id=current_user.id).all()
    len_bank_accounts = len(bank_accounts)
    formats = FormatMoney.query.all()
    return render_template('register_bank_account.html', len_bank_accounts=len_bank_accounts, formats=formats, bank=bank, type=type)


@app.route('/<string:bank_name>/account/<int:account_id>')
def visit_bank_account(bank_name, account_id):
    """ This is the visiting the bank account function """
    bank = Bank.query.filter_by(name=bank_name).first()
    bank_account = BankAccount.query.filter_by(bank_id=bank.id, id=account_id).first()

    return render_template('bank_account.html', bank_account=bank_account, bank=bank)


def transact_different_formats(account_1, account_2, amount):
    account_2.balance += amount / 12341
    account_2.balance = round(account_2.balance, 2)
    account_1.balance -= amount
    db.session.commit()


@app.route('/<bank_name>/transaction/<int:account_id>', methods=['POST', 'GET'])
def transaction(bank_name, account_id):
    """ This is the transaction function for share a money between two bank accounts """
    bank = Bank.query.filter_by(name=bank_name).first()
    bank_account = BankAccount.query.filter_by(bank_id=bank.id, id=account_id).first()
    if request.method == 'POST':
        account_number = request.form.get('account_number').strip()
        amount = request.form.get('amount').strip()

        if not account_number or not amount:
            flash('Please complete the form!', category='warning')
            return redirect(url_for('transaction', bank_name=bank_name, account_id=account_id))

        account_number = int(account_number)
        amount = int(amount)

        user_account = BankAccount.query.filter_by(bank_id=bank.id, id=account_id).first()

        if amount >= user_account.balance:
            flash('You\'re balance not enought money!', category='warning')
            return redirect(url_for('transaction', bank_name=bank_name, account_id=account_id))

        account = BankAccount.query.filter_by(account_number=account_number).first()

        if not account:
            flash('No account exists with this number!', category='danger')
            return redirect(url_for('transaction', bank_name=bank_name, account_id=account_id))

        if user_account.account_number == account.account_number:
            flash('You\'re can\'t transaction to your own account from that account!', category='danger')
            return redirect(url_for('transaction', bank_name=bank_name, account_id=account_id))

        if user_account.format == 'UZS' and account.type == 'Vista' and account.format == 'USD':
            transact_different_formats(user_account, account, amount)

            flash('Transaction successfully completed!', category='success')
            return redirect(url_for('bank_home', bank_name=bank_name))

        if user_account.format != account.format:
            flash('You can\'t transaction to the different type of money to the one account!', category='danger')
            return redirect(url_for('transaction', bank_name=bank_name, account_id=account_id))

        account.balance += amount
        user_account.balance -= amount

        db.session.commit()

        flash('Transaction successfully completed!', category='success')
        return redirect(url_for('bank_home', bank_name=bank_name))

    return render_template('transaction.html', bank_name=bank_name, bank=bank, account=bank_account)


@app.route('/<string:bank_name>/register/bank-account/customize', methods=['POST', 'GET'])
def customize_account_type(bank_name):
    bank = Bank.query.filter_by(name=bank_name).first()
    types = Type.query.all()

    return render_template('customize_account.html', bank=bank, types=types)


@app.route('/<string:bank>/account/<int:id>/card/view')
def card_view(bank, id):
    bank = Bank.query.filter_by(name=bank).first()
    account = BankAccount.query.filter_by(bank_id=bank.id, id=id).first()
    type = Type.query.filter_by(title_type=account.type).first()
    time = datetime.now()
    account_number = str(account.account_number)
    return render_template('card_view.html', account_number=account_number, time=time, account=account, type=type)
