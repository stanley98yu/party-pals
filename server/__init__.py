#!/usr/bin/env python2.7
"""Main Flask server for running web application."""

import os
import traceback
import re
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, session, flash
from flask_socketio import SocketIO
import time
import datetime

# The database URI should be in the format: postgresql://<db-user>:<pass>@<server-ip>/<db-name>
DB_USER = 'sy2751'
DB_PASSWORD = '1o92684o'
DB_SERVER = 'w4111.cisxo09blonu.us-east-1.rds.amazonaws.com'
DATABASE_URI = 'postgresql://' + DB_USER + ':' + DB_PASSWORD + '@' + DB_SERVER + '/w4111'

# Application and Socket.io.
tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
app.secret_key = 'secret'
socketio = SocketIO(app)
engine = create_engine(DATABASE_URI) # Create an Engine object that connects to the DBAPI and the database.

# Modules
from server import comment, videos

# Create table test and insert values.
engine.execute("""DROP TABLE IF EXISTS test2, test_participate;""")

engine.execute("""
           CREATE TABLE IF NOT EXISTS test_participate (
               pid integer,
               uid serial,
               join_time timestamp without time zone
           );
           """)

@app.before_request
def before_request():
    """Set up database connection before every web request."""
    try:
        g.conn = engine.connect()
    except:
        print 'Problem connecting to the database.'
        traceback.print_exc()
        g.conn = None

@app.teardown_request
def teardown_request(exception):
    """Closes the database connection at the end of every web request."""
    try:
        g.conn.close()
    except:
        pass

@app.route('/')
def index():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        # if 'credentials' not in session:
        #     return redirect('/authorize')
        context = dict(username=session['username'])
        return render_template('index.html', **context)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        post_username = str(request.form['username'])
        post_password = str(request.form['password'])
        stmt = text("""
                    SELECT * FROM users
                    where username = :username AND password = :password
                    """)
        stmt = stmt.bindparams(bindparam("username", type_=String), bindparam("password", type_=String))
        cursor = g.conn.execute(stmt, {"username": post_username, "password": post_password})
        res = cursor.fetchall()
        if len(res):
            session['logged_in'] = True
            session['username'] = post_username
            for r in res:
                uid = r['uid']
                session['uid'] = uid
                print "uid" + str(uid)
        else:
            flash('Wrong password!')
        cursor.close()
        return index()
    else:
        return render_template('login.html')

@app.route("/logout")
def logout():
    session['logged_in'] = False
    return redirect('/')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        post_username = str(request.form['username'])
        post_password = str(request.form['password'])
        post_email = str(request.form['email'])
        post_dob = str(request.form['dob'])
        if not re.match(r'[0-9]{4}-[0-9]{2}-[0-9]{2}', post_dob):
            flash('Bad birthdate!')
            return render_template('signup.html')

        cursor = g.conn.execute("""SELECT uid FROM users ORDER BY uid DESC LIMIT 1""")
        uid = cursor.fetchone()['uid'] + 1

        stmt = text("""
                    INSERT INTO users(uid, username, password, email, date_of_birth) VALUES
                    (:uid, :username, :password, :email, :dob)
                    """)
        stmt = stmt.bindparams(bindparam("uid", type_=Integer), \
                               bindparam("username", type_=String), \
                               bindparam("password", type_=String), \
                               bindparam("email", type_=String), \
                               bindparam("dob", type_=String))
        cursor = g.conn.execute(stmt, {"uid": uid, \
                                       "username": post_username, \
                                       "password": post_password, \
                                       "email": post_email, \
                                       "dob": post_dob})
        cursor.close()
        return index()
    else:
        return render_template('signup.html')

@app.route('/p', methods=['POST'])
def party():
    post_pname = str(request.form['pname'])
    post_interests = str(request.form['interests'])

    # Insert interests into database.
    cursor = g.conn.execute("""SELECT interest_id FROM interest ORDER BY interest_id DESC LIMIT 1""")
    next_id = cursor.fetchone()['interest_id'] + 1
    for i in post_interests.split(','):
        stmt = text("""
                    INSERT INTO interest (interest_id, category, keyword) VALUES
                    (:next_id, :category, :keyword) ON CONFLICT DO NOTHING;
                    """)
        stmt = stmt.bindparams(bindparam("next_id", type_=Integer), \
                               bindparam("category", type_=String), \
                               bindparam("keyword", type_=String))
        if len(i) > 20:
            intrst = i[0:20]
        else:
            intrst = i
        cursor = g.conn.execute(stmt, {"next_id": next_id, "category": "other", "keyword": intrst})
        next_id += 1
    cursor.close()

    # Get uid from database.
    stmt = text("""
                SELECT * FROM users
                where username = :username
                """)
    stmt = stmt.bindparams(bindparam("username", type_=String))
    cursor = g.conn.execute(stmt, {"username": session['username']})
    res = cursor.fetchone()
    session['uid'] = res['uid']

    session['room'] = post_pname
    session['interests'] = post_interests
    return redirect('/party/' + post_pname)
