#!/usr/bin/env python2.7
"""Main Flask server for running web application."""

import os
import traceback
import click
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, session, flash

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
app.secret_key = b'secret'

# The database URI should be in the format: postgresql://<db-user>:<pass>@<server-ip>/<db-name>
DB_USER = 'sy2751'
DB_PASSWORD = 'secret'
DB_SERVER = 'w4111.cisxo09blonu.us-east-1.rds.amazonaws.com'
DATABASE_URI = 'postgresql://' + DB_USER + ':' + DB_PASSWORD + '@' + DB_SERVER + '/w4111'

# Create an Engine object that connects to the DBAPI and the database.
engine = create_engine(DATABASE_URI)

# Create table test and insert values.
engine.execute("""DROP TABLE IF EXISTS test;""")
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
                  ('yang', '1', 'yh2825@columbia.edu', '1997-03-04'),
                  ('eugene', '1', 'ew2493@columbia.edu', '1993-04-05');""")

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
    except Exception as e:
        pass

@app.route('/')
def index():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        context = dict(username=session['username'])
        return render_template('index.html', **context)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        post_username = str(request.form['username'])
        post_password = str(request.form['password'])

        cursor = g.conn.execute("""
                                SELECT * FROM test
                                WHERE username='%s' AND password='%s'
                                """ % (post_username, post_password))
        if list(cursor):
            session['logged_in'] = True
            session['username'] = post_username
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

        ins = """
              INSERT INTO test(username, password, email, date_of_birth) VALUES
              ('%s', '%s', '%s', '%s')
              """ % (post_username, post_password, post_email, post_dob)
        cursor = g.conn.execute(ins)
        cursor.close()
        return index()
    else:
        return render_template('signup.html')

if __name__ == '__main__':
    # Handles command line interface.
    @click.command()
    @click.option('--debug', is_flag=True)
    @click.option('--threaded', is_flag=True)
    @click.argument('host', default='0.0.0.0')
    @click.argument('port', default=8111, type=int)

    def run(host, port, debug, threaded):
        print "Running on %s:%d" % (host, port)
        app.run(host=host, port=port, debug=debug, threaded=threaded)

    run()
