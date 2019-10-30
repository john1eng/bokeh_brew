
# from main import *
from flask import render_template, request, url_for, flash, session, redirect

from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask import Blueprint

from models import Login, db
import logging
from flask_bcrypt import Bcrypt
from main import app

secur = Blueprint('secur', __name__)
bcrypt = Bcrypt(app)

@secur.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('bkapp_page'))
    error = None
    if request.method == 'POST':
        userN = request.form['username']
        passwN = request.form['password']

        import os
        # DATABASE_URL = os.environ['DATABASE_URL']
        import psycopg2
        db = psycopg2.connect(database = 'brewasis', host="127.0.0.1", port="5432", password="password", user="postgres")
        c = db.cursor()
        c.execute("select users from login where users= '{}'".format(userN))
        userN1 = c.fetchone()
        c.execute("select password from login where users= '{}'".format(userN))
        passwN1 = c.fetchone()

        try:
            if (userN != userN1[0]) or not(bcrypt.check_password_hash(passwN1[0], passwN)):
            # if (userN != userN1[0]) or (passwN != passwN1[0]):
                error = 'Invalid Credentials. Please try again.'
                c.execute("insert into loggings(users, entered)values('{}', '{}')".format(userN, 'unsuccessful'))
                db.commit()
                db.close()
            else:
                userlogin = Login.query.filter(Login.users == userN).first()
                login_user(userlogin)
                # next = flask.request.args.get('next')
                # # is_safe_url should check if the url is safe for redirects.
                # # See http://flask.pocoo.org/snippets/62/ for an example.
                # if not is_safe_url(next):
                #     return flask.abort(400)
                # session['logged_in'] = True
                c.execute("insert into loggings(users, entered)values('{}', '{}')".format(userN, 'successful'))
                db.commit()
                db.close()
                return redirect(url_for('bkapp_page'))
        except Exception as e:
            logging.error("Exception occurred", exc_info=True)
            error = 'Invalid Credentials. Please try again .'
            c.execute("insert into loggings(users, entered)values('{}', '{}')".format(userN, 'unsuccessful'))
            db.commit()
            db.close()

    return render_template('login.html', error=error)

@secur.route('/logout')
@login_required
def logout():
    logout_user()
    # session.pop('logged_in', None)
    flash('You were logged out.')
    return redirect(url_for('secur.login'))

@secur.route("/loggings", methods=['GET', 'POST'])
@login_required
def loggings():

    import os
    import psycopg2
    db = psycopg2.connect(database = 'brewasis', host="127.0.0.1", port="5432", password="password", user="postgres")
    c = db.cursor()
    c.execute('select * from loggings')

    # loggings = [dict(id=row[0],users=row[1],password=row[2],time=row[3])for row in reversed(c.fetchall())]
    loggings = [dict(id=row[0],users=row[1],entered=row[3],time=row[2])for row in reversed(c.fetchall())]
    db.close()

    return render_template('loggings.html',loggings=loggings)

@secur.route("/createUser", methods=['GET', 'POST'])
@login_required
def signup():
    error = None
    successful = None
    if request.method == 'POST':
        userN = request.form['username']
        passwN = request.form['password']
        keyN = request.form['key']
        try:
            # check errors - duplicate user
            if userN == (Login.query.filter(Login.users == userN).first()).users:
            # print(test.users)
                error = 'duplicate user name'

            # check errors - invalid secret key
        except:

            if keyN == (Login.query.filter(Login.users == 'secretkey').first()).password:
                # newUser = Login(users=userN, password=passwN)
                harshpass = bcrypt.generate_password_hash(passwN).decode('utf-8')
                newUser = Login(users=userN, password=harshpass)
                db.session.add(newUser)
                db.session.commit()
                successful = 'user created'
            else:
                error = 'invalid secret key'


    return render_template('createUser.html', error=error, successful=successful)
