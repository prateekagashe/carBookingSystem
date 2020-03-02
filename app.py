from __init__ import db, app, mysql, config
from flask import render_template, redirect, request, url_for, flash, Flask, session
import googlemaps, string, random
from flask_bcrypt import Bcrypt
import pymysql
import mysql.connector

import stripe

public_key = "pk_test_Mp2uO2uwzVZET5ILQmkhzK2K00QB7P6yX8"
stripe.api_key = "sk_test_wthgXH5S6lLfs2qPnhIDeSgo00aYhKfHwG"
bcrypt = Bcrypt()


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        if request.form['submit'] == 'book':
            session['dep_city'] = request.form['source']
            session['arr_city'] = request.form['destination']
            return redirect(url_for('welcome_user', dep_city=session['dep_city'], arr_city=session['arr_city']))
    return render_template('index.html')


@app.route('/select_driver/<dep_city>/<arr_city>', methods=['GET', 'POST'])
def welcome_user(dep_city, arr_city):
    if request.method == 'POST':
        if request.form['submit'] == 'driver':
            session['selected_driver'] = request.form['driver']
            print('driver', session['selected_driver'])
        return redirect(url_for('customer_detail'))

    gmaps = googlemaps.Client(key='AIzaSyCD-yOrwFqzEOo0U1Fk4BpQvFYDywP-jz0')
    dist = gmaps.distance_matrix(dep_city, arr_city)['rows'][0]['elements'][0]
    session['driver_details'] = fetch_driver()
    print('status', dist)
    if dist['status'] == 'ZERO_RESULTS':
        flash('Please enter correct destination')
        return redirect(url_for('home'))
    else:
        distance = dist['distance']['text'].replace(',', '').replace('km', '').replace('m', '').strip()
        print(distance)
        final_distance = float(distance)
        for rows in session['driver_details']:
            rows.append(rows[4] * final_distance)

        print(session['driver_details'])
        return render_template('drivers.html', driver_details=session['driver_details'])


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


@app.route('/customer_detail', methods=['GET', 'POST'])
def customer_detail():
    if 'loggedin' in session:
        user_detail = fetch_user()
        if request.method == 'POST':
            if request.form['submit'] == 'customer_detail':
                name = request.form['name']
                email = request.form['email']
                address = request.form['Address']
                locality = request.form['locality']
                time = request.form['time']
                mobile = request.form['mobile']
                session['id'] = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

                sql = """insert into tbl_booking(bookingid, driver_id, username, booking_name, email, address, locality, drop_point, pickup_time, mobile) 
                values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                conn = mysql.connector.connect(**config)
                cursor = conn.cursor()        
                cursor.execute(sql, (session['id'], session['selected_driver'], session['username'], name, email, address, locality, session['arr_city'], time, mobile))

                conn.commit()
                conn.close()
                cursor.close()
                return redirect(url_for('payment'))

        return render_template('contact.html', user_detail=user_detail)
    else:
        return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['submit'] == 'Login':
            user = request.form['uname']
            password = request.form['psw']

            sql = """select * from tbl_user where username = %s;"""
            conn = mysql.connector.connect(**config)
            cursor = conn.cursor()     
            cursor.execute(sql, (user,))
            rows = cursor.fetchall()
            print("from sql", rows)
            conn.close()
            cursor.close()
            print(rows)
            if len(rows) != 0:
                for item in rows:
                    print(item)
                    print('test', item[5], password)
                    check = bcrypt.check_password_hash(item[5], password)
                    if check:
                        session['loggedin'] = True
                        session['username'] = user
                        return redirect(url_for('customer_detail'))
                    else:
                        flash('Incorrect Password')
            else:
                flash('Incorrect UserName')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if request.form['submit'] == 'register':
            firstname = request.form['firstName']
            lastname = request.form['lastName']
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            mobile = request.form['mobile']
            hashed_password = bcrypt.generate_password_hash(password=password)

            sql = """insert into tbl_user(firstName, lastName, username, email, user_password, mobile) values
            (%s, %s, %s, %s, %s, %s)"""
            try:
                conn = mysql.connector.connect(**config)
                cursor = conn.cursor()               
                cursor.execute(sql, (firstname, lastname, username, email, hashed_password, mobile,))
                conn.commit()
                conn.close()
                cursor.close()
            except mysql.connector.Error as err:
                print(err)
                if 'email' in str(err):
                    flash('Email Id already used..please use a different emailId')
                else:
                    flash('Username already used please try again with a different username')
                return render_template('register.html')
            return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/payment', methods=['GET', 'POST'])
def payment():
    return render_template('payment.html', public_key=public_key)


@app.route('/payments', methods=['post'])
def final_payment():
    return render_template('confirmation.html')


@app.route('/booking_confirm', methods=['GET', 'POST'])
def confirmation():
    customer = stripe.Customer.create(email=request.form['stripeEmail'],
                                      source=request.form['stripeToken'])

    charge = stripe.Charge.create(
        customer=customer.id,
        amount=1999,
        currency='inr',
        description='Donation'
    )
    booking_detail, driver_detail = fetch_booking()
    print(booking_detail)
    print(session['driver_detail'])
    return render_template('confirmation.html', booking_detail=booking_detail, driver=session['driver_detail'])


def fetch_driver():
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    cursor.execute("select * from tbl_driver_details")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    print(rows)
    driver_list = []
    for item in rows:
        driver_list.append(list(item))
    print(driver_list)
    return driver_list


def fetch_user():
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()    
    cursor.execute("""select * from tbl_user where username = %s;""", (session['username'],))
    rows = cursor.fetchone()
    cursor.close()
    conn.close()
    print(rows)
    user_detail = list(rows)

    return user_detail


def fetch_booking():
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor(buffered=True)
    cursor.execute("""select * from tbl_booking where username = %s and bookingId = %s;""", (session['username'], session['id'],))
    rows = cursor.fetchone()
    cursor.execute("""select * from tbl_driver_details where driver_id = %s;""", (session['selected_driver'],))
    row1 = cursor.fetchone()
    print(rows)
    cursor.close()
    conn.close()
    booking_detail = list(rows)
    session['driver_detail'] = list(row1)
    return booking_detail, session['driver_detail']


if __name__ == '__main__':
    app.run(debug=True)



