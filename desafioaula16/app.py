from datetime import datetime
from unicodedata import category, name
from flask_restful import Api, Resource, reqparse
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from flask import Flask, request, render_template, redirect, flash, url_for, jsonify, abort, session, send_from_directory
from dao import RestaurantDao, UserDao
from flask_mysqldb import MySQL 
from models import Restaurant, User 
import os

app = Flask(__name__)
app.secret_key = 'NEXT'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['MYSQL_HOST'] = "0.0.0.0"
app.config['MYSQL_USER'] = "root"
# app.config['MYSQL_PASSWORD'] = "admin"
app.config['MYSQL_DB'] = "models"
app.config['MYSQL_PORT'] = 3306
app.config['UPLOAD_PATH'] = os.path.dirname(os.path.abspath(__file__)) + '/uploads'

api = Api(app)
db = SQLAlchemy(app)

db = MySQL(app)

restaurant_dao = RestaurantDao(db)
user_dao = UserDao(db)

@app.route('/')
def home():
    list = restaurant_dao.list()
    return render_template('lista.html', titulo = 'All Food Restaurant NExT - Orders ', orders=list) 

@app.route('/new')
def new():
    if 'user_logon' not in session or session['user_logon'] == None:
        return redirect(url_for('login', proxima=url_for('new')))
    return render_template('new.html', titulo='All Food Restaurant NExT - New Order')

@app.route('/createorder', methods=['POST'])
def create_order():
    plate = request.form['plate']
    category = request.form['category']
    price = request.form['price']
    order = Restaurant(plate, category, price)
    order = restaurant_dao.save(order)

    file=request.files['file']
    upload_path = app.config['UPLOAD_PATH']
    file.save(f'{upload_path}/image{order.id}.jpg')
    return redirect(url_for('home'))

@app.route('/edit/<int:id>')
def edit(id):
    if 'user_logon' not in session or session['user_logon'] == None:
        return redirect(url_for('login', proxima=url_for('edit')))
    order = restaurant_dao.search_by_id(id)
    return render_template('edit.html', titulo='All Food Restaurant NExT - Edit Order', order=order, front_image = f'front{id}.jpg')

@app.route('/update', methods=['POST'])
def update():
    plate = request.form['plate']
    category = request.form['category']
    price = request.form['price']
    order = Restaurant(plate, category, price, id=request.form['id'])
    restaurant_dao.save(order)
    return redirect(url_for('home')) 

@app.route('/delete/<int:id>')
def delete(id):
    restaurant_dao.delete(id)
    flash('Order has been removed')
    return redirect(url_for('home'))

@app.route('/login')
def login():
    next = request.args.get('next')
    return render_template('login.html', next=next)

@app.route('/authentication', methods=['POST'])
def authentication():
    user = user_dao.search_by_id(request.form['user'])
    if user: 
        if user.password ==request.form['password']: 
            session ['user_logon'] = user.id 
            flash(user.name + ' login successful!')
            next_page = request.form['next']
            return redirect(next_page)
    else:
        flash('Please, Try again!')
        return redirect(url_for('login'))

@app.route('/signup')
def signup():
    next1 = request.args.get('next1')
    return render_template('signup.html', next1=next1)

@app.route('/logout')
def logout():
    session ['user_logon'] = None
    flash('No user logon')
    return redirect(url_for('home'))

@app.route('/uploads/<file_name>')
def image(file_name):
    return send_from_directory('uploads', file_name)
   

if __name__ == '__main__':
    app.run(debug=True)
    