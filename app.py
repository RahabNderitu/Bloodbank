from flask import render_template
import sqlite3
import requests
from flask import Flask
from flask import request, redirect, url_for, session, flash
from flask_wtf import Form
from wtforms import TextField
import joblib
import pandas as pd
import os
import numpy as np
import re

app = Flask(__name__)
app.secret_key = "super secret key"

model = joblib.load('knnmodel.pkl')
from sklearn import metrics


@app.route('/predict/<id>', methods=('GET', 'POST'))
def predict(id):

    if request.method == 'GET':
        con = sqlite3.connect('database.db')
        con.row_factory = sqlite3.Row

        cur = con.cursor()
        cur.execute("select * from blood where id=?", (id, ))


        rows = cur.fetchall()

        for x in rows:
            user = x[6]
            print("usernameeeeee: " + user)
            cur.execute("select * from users where email=?", (user, ))

            users = cur.fetchall()


        return render_template("editdonor.html", rows=rows,users=users)
    if request.method == 'POST':

        recency = int(request.form['recency'])
        frequency = int(request.form['frequency'])
        total = int(request.form['total'])
        time = int(request.form['time'])


      


        input_data = [{
            'Recency (months)': recency,
            'Frequency (times) ': frequency,
            'Monetary (c.c. blood)': total,
            'Time (months)': time
        }]
        data = pd.DataFrame(input_data)
        print(data)
        data = data.to_numpy()
        print(data)

        label = {0: 'No', 1: 'Yes'}
        logreg = model.predict(data)[0]
        resfinal = label[logreg]
        print(logreg)

        con = sqlite3.connect('database.db')
        con.row_factory = sqlite3.Row

        cur = con.cursor()
        cur.execute("select * from blood where id=?", (id, ))

        rows = cur.fetchall()
        for x in rows:
            user = x[6]
            print("usernameeeeee" + user)

            cur.execute("select * from users where email=?", (user, ))

            users = cur.fetchall()


        return render_template(
            'editdonor.html',
            prediction_text='Donation chance: {}'.format(logreg),
            rows=rows,users=users)


@app.route('/')
def hel():
    conn = sqlite3.connect('database.db')
    print("Opened database successfully")
    conn.execute(
        'CREATE TABLE IF NOT EXISTS users (lastdonation TEXT,frequency TEXT,totaldonation INTEGER,monthssincefirst TEXT,name TEXT, addr TEXT, city TEXT, pin TEXT, bg TEXT,email TEXT UNIQUE, pass TEXT)'
    )
    print("Table created successfully")
    conn.close()
    if session.get('username') == True:
        messages = session['username']

    else:
        messages = ""
    user = {'username': messages}
    return redirect(url_for('index', user=user))


@app.route('/reg')
def add():
    return render_template('register.html')


@app.route('/addrec', methods=['POST', 'GET'])
def addrec():
    msg = ""
    #con = None
    if request.method == 'POST':
        try:
            lastdonation = request.form['lastdonation']
            frequency = request.form['frequency']
            totaldonation = request.form['totaldonation']
            monthssincefirst = request.form['monthssincefirst']

            nm = request.form['nm']
            addr = request.form['add']
            city = request.form['city']
            pin = request.form['pin']
            bg = request.form['bg']
            email = request.form['email']
            passs = request.form['pass']

            with sqlite3.connect("database.db") as con:
                cur = con.cursor()
                cur.execute(
                    "INSERT INTO users (lastdonation,frequency,totaldonation,monthssincefirst,name,addr,city,pin,bg,email,pass) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                    (lastdonation, frequency, totaldonation, monthssincefirst,
                     nm, addr, city, pin, bg, email, passs))
                con.commit()
                msg = "Record successfully added"

        except:
            con.rollback()
            msg = "error in insert operation"

        finally:
            flash('done')
            return redirect(url_for('index'))
            con.close()


@app.route('/index', methods=['POST', 'GET'])
def index():

    if request.method == 'POST':
        if session.get('username') is not None:
            messages = session['username']

        else:
            messages = ""
        user = {'username': messages}
        print(messages)
        val = request.form['search']
        print(val)
        type = request.form['type']
        print(type)
        if type == 'blood':
            con = sqlite3.connect('database.db')
            con.row_factory = sqlite3.Row

            cur = con.cursor()
            cur.execute("select * from users where bg=?", (val, ))
            search = cur.fetchall()
            cur.execute("select * from users ")

            rows = cur.fetchall()
            users = cur.fetchall()

            return render_template('index2.html',
                                   title='Home',
                                   user=user,
                                   rows=rows,
                                   search=search)

        if type == 'donorname':
            con = sqlite3.connect('database.db')
            con.row_factory = sqlite3.Row

            cur = con.cursor()
            cur.execute("select * from users where name=?", (val, ))
            search = cur.fetchall()
            cur.execute("select * from users ")

            rows = cur.fetchall()

            return render_template('index2.html',
                                   title='Home',
                                   user=user,
                                   rows=rows,
                                   search=search)

    if session.get('username') is not None:
        messages = session['username']

    else:
        messages = ""
    user = {'username': messages}
    print(messages)
    if request.method == 'GET':
        con = sqlite3.connect('database.db')
        con.row_factory = sqlite3.Row

        cur = con.cursor()
        cur.execute("select * from users ")

        rows = cur.fetchall()
        return render_template('index2.html',
                               title='Home',
                               user=user,
                               rows=rows)

    #messages = request.args['user']


@app.route('/list')
def list():
    con = sqlite3.connect('database.db')
    con.row_factory = sqlite3.Row

    cur = con.cursor()
    cur.execute("select * from users")

    rows = cur.fetchall()
    print(rows)
    return render_template("list.html", rows=rows)


@app.route('/drop')
def dr():
    con = sqlite3.connect('database.db')
    con.execute("DROP TABLE request")
    return "dropped successfully"


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('/login.html')
    if request.method == 'POST':

        email = request.form['email']
        password = request.form['pass']
        if email == 'admin@bloodbank.com' and password == 'admin':
            a = 'yes'
            session['username'] = email
            #session['logged_in'] = True
            session['admin'] = True
            return redirect(url_for('index'))
        #print((password,email))
        con = sqlite3.connect('database.db')
        con.row_factory = sqlite3.Row

        cur = con.cursor()
        cur.execute("select email,pass from users where email=?", (email, ))
        rows = cur.fetchall()
        for row in rows:
            print(row['email'], row['pass'])
            a = row['email']
            session['username'] = a
            session['logged_in'] = True
            print(a)
            u = {'username': a}
            p = row['pass']
            print(p)

            if email == a and password == p:
                return redirect(url_for('index'))
            else:
                return render_template('/login.html')
        return render_template('/login.html')
    else:
        return render_template('/')


@app.route('/logout')
def logout():
    # remove the username from the session if it is there
    session.pop('username', None)
    session.pop('logged_in', None)
    try:
        session.pop('admin', None)
    except KeyError as e:
        print("I got a KeyError - reason " + str(e))

    return redirect(url_for('login'))


@app.route('/dashboard')
def dashboard():
    totalblood = 0
    con = sqlite3.connect('database.db')
    con.row_factory = sqlite3.Row

    cur = con.cursor()
    cur.execute("select * from blood")

    rows = cur.fetchall()
    for row in rows:
        number = re.sub(r"\D", "", (row['qty']))

        totalblood += int(number)

    cur.execute("select * from users")
    users = cur.fetchall()

    Apositive = 0
    Opositive = 0
    Bpositive = 0
    Anegative = 0
    Onegative = 0
    Bnegative = 0
    ABpositive = 0
    ABnegative = 0

    print(rows)
    cur.execute("select * from blood where type=?", ('A+', ))
    type = cur.fetchall()
    for a in type:
        # Apositive += int(a['qty'])

        number = re.sub(r"\D", "", (row['qty']))

        Apositive += int(number)

    cur.execute("select * from blood where type=?", ('A-', ))
    type = cur.fetchall()
    for a in type:
        # Anegative += int(a['qty'])

        number = re.sub(r"\D", "", (row['qty']))

        Anegative += int(number)

    cur.execute("select * from blood where type=?", ('O+', ))
    type = cur.fetchall()
    for a in type:
        # Opositive += int(a['qty'])

        number = re.sub(r"\D", "", (row['qty']))

        Opositive += int(number)

    cur.execute("select * from blood where type=?", ('O-', ))
    type = cur.fetchall()
    for a in type:

        number = re.sub(r"\D", "", (row['qty']))

        Onegative += int(number)
        # Onegative += int(a['qty'])

    cur.execute("select * from blood where type=?", ('B+', ))
    type = cur.fetchall()
    for a in type:
        # Bpositive += int(a['qty'])
        number = re.sub(r"\D", "", (row['qty']))

        Bpositive += int(number)

    cur.execute("select * from blood where type=?", ('B-', ))
    type = cur.fetchall()
    for a in type:
        # Bnegative += int(a['qty'])
        number = re.sub(r"\D", "", (row['qty']))

        Bnegative += int(number)

    cur.execute("select * from blood where type=?", ('AB+', ))
    type = cur.fetchall()
    for a in type:
        # ABpositive += int(a['qty'])
        number = re.sub(r"\D", "", (row['qty']))

        ABpositive += int(number)

    cur.execute("select * from blood where type=?", ('AB-', ))
    type = cur.fetchall()
    for a in type:
        # ABnegative += int(a['qty'])
        number = re.sub(r"\D", "", (row['qty']))

        ABnegative += int(number)

    bloodtypestotal = {
        'apos': Apositive,
        'aneg': Anegative,
        'opos': Opositive,
        'oneg': Onegative,
        'bpos': Bpositive,
        'bneg': Bnegative,
        'abpos': ABpositive,
        'abneg': ABnegative
    }

    return render_template("requestdonors.html",
                           rows=rows,
                           totalblood=totalblood,
                           users=users,
                           bloodtypestotal=bloodtypestotal)


@app.route('/bloodbank')
def bl():
    conn = sqlite3.connect('database.db')
    print("Opened database successfully")
    conn.execute(
        'CREATE TABLE IF NOT EXISTS blood (id INTEGER PRIMARY KEY AUTOINCREMENT,lastdonation TEXT,frequency TEXT,totaldonation TEXT,monthssincefirst TEXT, type TEXT, donorname TEXT, donorsex TEXT, qty TEXT, dweight TEXT, donoremail TEXT, phone TEXT)'
    )
    print("Table created successfully")
    conn.close()
    return render_template('/adddonor.html')


@app.route('/addb', methods=['POST', 'GET'])
def addb():
    msg = ""
    if request.method == 'POST':
        try:

            lastdonation = request.form['lastdonation']
            frequency = request.form['frequency']
            totaldonation = request.form['totaldonation']
            monthssincefirst = request.form['monthssincefirst']

            type = request.form['blood_group']
            donorname = request.form['donorname']
            donorsex = request.form['gender']
            qty = request.form['qty']
            dweight = request.form['dweight']
            email = request.form['email']
            phone = request.form['phone']

            with sqlite3.connect("database.db") as con:
                cur = con.cursor()
                cur.execute(
                    "INSERT INTO blood (lastdonation,frequency,totaldonation,monthssincefirst,type,donorname,donorsex,qty,dweight,donoremail,phone) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                    (lastdonation,frequency,totaldonation,monthssincefirst,type, donorname, donorsex, qty, dweight, email, phone))
                con.commit()
                msg = "Record successfully added"

            with sqlite3.connect("database.db") as conn2:
                cur = conn2.cursor()
                cur.execute(
                    "UPDATE user SET  totaldonation = totaldonation + 1 WHERE email = ?",
                    (email))

                con.commit()
                msg = "Record successfully updated"

        except:
            con.rollback()
            msg = "error in insert operation"

        finally:
            flash("added new entry!")
            return redirect(url_for('dashboard'))
            con.close()

    else:
        return render_template("rest.html", msg=msg)


@app.route("/editdonor/<id>", methods=('GET', 'POST'))
def editdonor(id):
    msg = ""
    qtty = 0
    fqe=0
    if request.method == 'GET':
        con = sqlite3.connect('database.db')
        con.row_factory = sqlite3.Row

        cur = con.cursor()
        cur.execute("select * from blood where id=?", (id, ))

        rows = cur.fetchall()
        for row in rows:
            print(row[0])
            qtty = qtty + int(row[3])
            fqe=fqe+int(row[2])
            print("-----------")
            print(qtty)
            print(fqe)

        return render_template("editdonor.html", rows=rows,qtty=qtty,freq=fqe)
    if request.method == 'POST':
        try:
            type = request.form['blood_group']
            donorname = request.form['donorname']
            donorsex = request.form['gender']
            qty = request.form['qty']
            dweight = request.form['dweight']
            email = request.form['email']
            phone = request.form['phone']
            qtty= request.form['totaldonation']
            freq= request.form['frequency']

            total=int(qtty)+int(qty)
            freq_total=int(freq)+1
            print(total)

            with sqlite3.connect("database.db") as con:
                cur = con.cursor()
                cur.execute(
                    "UPDATE blood SET frequency=?,totaldonation=?,type = ?, donorname = ?, donorsex = ?, qty = ?,dweight = ?, donoremail = ?,phone = ? WHERE id = ?",
                    (freq_total, total,type, donorname, donorsex, qty, dweight, email, phone,
                     id))
                con.commit()
                msg = "Record successfully updated"

        except:
            con.rollback()
            msg = "error in insert operation"

        finally:
            flash('saved successfully')
            return redirect(url_for('dashboard'))
            con.close()


@app.route("/myprofile/<email>", methods=('GET', 'POST'))
def myprofile(email):
    msg = ""
    if request.method == 'GET':

        con = sqlite3.connect('database.db')
        con.row_factory = sqlite3.Row

        cur = con.cursor()
        cur.execute("select * from users where email=?", (email, ))
        rows = cur.fetchall()
        return render_template("myprofile.html", rows=rows)
    if request.method == 'POST':
        try:
            name = request.form['name']
            addr = request.form['addr']
            city = request.form['city']
            pin = request.form['pin']
            bg = request.form['bg']
            emailid = request.form['email']

            print(name, addr)

            with sqlite3.connect("database.db") as con:
                cur = con.cursor()
                cur.execute(
                    "UPDATE users SET name = ?, addr = ?, city = ?, pin = ?,bg = ?, email = ? WHERE email = ?",
                    (name, addr, city, pin, bg, emailid, email))
                con.commit()
                msg = "Record successfully updated"
        except:
            con.rollback()
            msg = "error in insert operation"

        finally:
            flash('profile saved')
            return redirect(url_for('index'))
            con.close()


@app.route('/contactforblood/<emailid>', methods=('GET', 'POST'))
def contactforblood(emailid):
    if request.method == 'GET':
        conn = sqlite3.connect('database.db')
        print("Opened database successfully")
        conn.execute(
            'CREATE TABLE IF NOT EXISTS request (id INTEGER PRIMARY KEY AUTOINCREMENT, toemail TEXT, formemail TEXT, toname TEXT, toaddr TEXT)'
        )
        print("Table created successfully")
        fromemail = session['username']
        name = request.form['nm']
        addr = request.form['add']

        print(fromemail, emailid)
        conn.execute(
            "INSERT INTO request (toemail,formemail,toname,toaddr) VALUES (?,?,?,?)",
            (emailid, fromemail, name, addr))
        conn.commit()
        conn.close()
        flash('request sent')
        return redirect(url_for('index'))
    if request.method == 'POST':
        conn = sqlite3.connect('database.db')
        print("Opened database *** successfully")
        conn.execute(
            'CREATE TABLE IF NOT EXISTS request (id INTEGER PRIMARY KEY AUTOINCREMENT, toemail TEXT, formemail TEXT, toname TEXT, toaddr TEXT)'
        )
        print("Table created successfully")
        fromemail = session['username']
        name = request.form['nm']
        addr = request.form['add']

        print(fromemail, emailid)
        conn.execute(
            "INSERT INTO request (toemail,formemail,toname,toaddr) VALUES (?,?,?,?)",
            (emailid, fromemail, name, addr))
        conn.commit()
        conn.close()
        flash('request sent')
        return redirect(url_for('index'))


@app.route('/notifications', methods=('GET', 'POST'))
def notifications():
    if request.method == 'GET':

        conn = sqlite3.connect('database.db')
        print("Opened database successfully")
        print((session['username'], ))
        conn.row_factory = sqlite3.Row

        cur = conn.cursor()
        cor = conn.cursor()
        cur.execute('select * from request where toemail=?',
                    (session['username'], ))
        cor.execute('select * from request where toemail=?',
                    (session['username'], ))
        row = cor.fetchone()
        rows = cur.fetchall()
        print(rows)

        if row == None:
            return render_template('notifications.html')
        else:
            return render_template('notifications.html', rows=rows)


@app.route('/deleteuser/<useremail>', methods=('GET', 'POST'))
def deleteuser(useremail):
    if request.method == 'GET':
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        cur.execute('delete from users Where email=?', (useremail, ))
        flash('deleted user:' + useremail)
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))


@app.route('/deletebloodentry/<id>', methods=('GET', 'POST'))
def deletebloodentry(id):
    if request.method == 'GET':
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        cur.execute('delete from blood Where id=?', (id, ))
        flash('deleted entry:' + id)
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))


@app.route('/deleteme/<useremail>', methods=('GET', 'POST'))
def deleteme(useremail):
    if request.method == 'GET':
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        cur.execute('delete from users Where email=?', (useremail, ))
        flash('deleted user:' + useremail)
        conn.commit()
        conn.close()
        session.pop('username', None)
        session.pop('logged_in', None)
        return redirect(url_for('index'))


@app.route('/deletenoti/<id>', methods=('GET', 'POST'))
def deletenoti(id):
    if request.method == 'GET':
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        cur.execute('delete from request Where id=?', (id, ))
        flash('deleted notification:' + id)
        conn.commit()
        conn.close()
        return redirect(url_for('notifications'))


if __name__ == '__main__':
    app.run(debug=True)
