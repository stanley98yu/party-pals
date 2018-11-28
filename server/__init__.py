#!/usr/bin/env python2.7
"""Main Flask server for running web application."""

import os
import traceback
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, session, flash
from flask_socketio import SocketIO
import time
import datetime

# The database URI should be in the format: postgresql://<db-user>:<pass>@<server-ip>/<db-name>
DB_USER = 'sy2751'
DB_PASSWORD = 'secret'
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
engine.execute("""DROP TABLE IF EXISTS test2, test, test_participate;""")
engine.execute("""
               CREATE TABLE IF NOT EXISTS test (
                   uid serial,
                   username text NOT NULL,
                   password text NOT NULL,
                   email text NOT NULL,
                   date_of_birth date NOT NULL,
                   PRIMARY KEY (uid)
               );
               """)
engine.execute("""INSERT INTO test(username, password, email, date_of_birth) VALUES
                  ('stanley', '1', 'stanley.yu@columbia.edu', '1998-12-01'),
                  ('yang', '1', 'yh2825@columbia.edu', '1997-03-04');""")

engine.execute("""
           CREATE TABLE IF NOT EXISTS test2 (
               pid integer,
               uid serial,
               party_name text NOT NULL,
               PRIMARY KEY (pid),
               FOREIGN KEY (uid) REFERENCES test(uid)
           );
           """)
engine.execute("""INSERT INTO test2(pid, uid, party_name) VALUES
              (0001, 1, 'test'),
              (0002, 2, 'test2');""")

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

        # cursor = g.conn.execute("""
        #                        SELECT * FROM test
        #                        WHERE username='%s' AND password='%s'
        #                        """ % (post_username, post_password))
        
	stmt = text("""
                    SELECT * FROM test
                    where username = :username AND password = :password
                    """)
        stmt = stmt.bindparams(bindparam("username", type_=String), bindparam("password", type_=String))
        cursor = g.conn.execute(stmt, {"username": post_username, "password": post_password})	

	if len(cursor.fetchall()):
            session['logged_in'] = True
            session['username'] = post_username
	    for result in cursor:
		uid = result['uid']
	    	session['uid'] = uid
		print("uid" + str(uid))
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

        #ins = """
        #      INSERT INTO test(username, password, email, date_of_birth) VALUES
        #      ('%s', '%s', '%s', '%s')
        #      """ % (post_username, post_password, post_email, post_dob)
        #cursor = g.conn.execute(ins)
        stmt = text("""
                    INSERT INTO test(username, password, email, date_of_birth) VALUES
                    (:username, :password, :email, :dob)
                    """)
        stmt = stmt.bindparams(bindparam("username", type_=String), \
                               bindparam("password", type_=String), \
                               bindparam("email", type_=String), \
                               bindparam("dob", type_=String))
        cursor = g.conn.execute(stmt, {"username": post_username, \
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
    
    session['room'] = post_pname
    session['interests'] = post_interests
    return redirect('/party/' + post_pname)
