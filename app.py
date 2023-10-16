from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from datetime import datetime, date
import random
import string
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ERP.db'
app.secret_key = 'ERP@321'

db = SQLAlchemy(app)

app.config['SESSION_TYPE'] = 'filesystem'
Session(app)


class Customers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    WalletCode = db.Column(db.String(60))
    Name = db.Column(db.String(40))
    Phone = db.Column(db.String(11))
    Addres = db.Column(db.String(200))
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    sales_transactions = db.relationship('SalesTransactions', backref='customer', lazy=True)

class Products(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(60))
    Barcode = db.Column(db.String(40))
    Price = db.Column(db.Integer)
    SPrice = db.Column(db.Integer)
    IPrice = db.Column(db.Integer)
    Quantity = db.Column(db.Integer)
    SupplierID = db.Column(db.Integer, db.ForeignKey('suppliers.id'))
    SupplierName = db.Column(db.String(200))
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
class Suppliers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(60))
    Phone = db.Column(db.String(11))
    WalletCode = db.Column(db.String(60))
    products = db.relationship('Products', backref='supplier', lazy=True)
class SalesTransactions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Barcode = db.Column(db.String(40))
    Paid = db.Column(db.Integer)
    Remaining = db.Column(db.Integer)
    TotalAmount = db.Column(db.Integer)
    Done = db.Column(db.Integer)
    PayType = db.Column(db.Integer)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
class SItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    SBarcode = db.Column(db.String(40))
    ProductsId = db.Column(db.Integer)
    ProductsName = db.Column(db.String(60))
    Quantity = db.Column(db.Integer)
class ProductInstallments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    SBarcode = db.Column(db.String(40))
    CustomerID = db.Column(db.Integer)
    InstallmentAmount = db.Column(db.Integer)
    InstallmentDueDate = db.Column(db.DateTime(timezone=True))
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' in session and session['username'] == 'admin':
            return f(*args, **kwargs)
        return redirect(url_for('login'))

    return decorated_function
def generate_unique_code(length=20):
    characters = string.ascii_letters + string.digits
    unique_code = ''.join(random.choice(characters) for _ in range(length))
    return unique_code

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'admin' and password == '123':
            session['username'] = username
            return redirect("/")
        else:
            return render_template('login.html', message='Invalid credentials')

    return render_template('login.html')


@app.route('/')
@admin_required
def home():
    return render_template('index.html')


@app.route('/users')
@admin_required
def users():
    Users = Customers.query.all()
    return render_template('users.html',users=Users)
@app.route('/sups')
@admin_required
def sups():
    Users = Suppliers.query.all()
    return render_template('sups.html',users=Users)

@app.route("/addprod",methods=['POST', 'GET'])
def addprod():
    sups = Suppliers.query.all()
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        addres = request.form.get('addres')
        NewCus = Customers(Name=name,  # Use the correct column names (Name, Phone, Addres)
                           Phone=phone,
                           Addres=addres,
                           WalletCode=generate_unique_code())
        db.session.add(NewCus)
        db.session.commit()
        return render_template('addprod.html', mes=f'تمت اضافت {name} بنجاح',sups=sups)
    return render_template('addprod.html',sups=sups)
@app.route("/adduser", methods=['POST', 'GET'])
def adduser():
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        addres = request.form.get('addres')
        NewCus = Customers(Name=name,  # Use the correct column names (Name, Phone, Addres)
                           Phone=phone,
                           Addres=addres,
                           WalletCode=generate_unique_code())
        db.session.add(NewCus)
        db.session.commit()
        return render_template('adduser.html', mes=f'تمت اضافت {name} بنجاح')
    return render_template('adduser.html')

@app.route("/addsup", methods=['POST', 'GET'])
def addsup():
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
       
        NewCus = Suppliers(Name=name,
                           Phone=phone,
                           WalletCode=generate_unique_code())
        db.session.add(NewCus)
        db.session.commit()
        return render_template('adduser.html', mes=f'تمت اضافت {name} بنجاح')
    return render_template('addsup.html')
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))
@app.route("/delet/<int:id>")
def delet(id):
    Cus = Customers.query.get_or_404(id)
    db.session.delete(Cus)
    db.session.commit()
    return redirect('/users')
@app.route("/setting")
def setting():
    return render_template('setting.html')
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=7001)
