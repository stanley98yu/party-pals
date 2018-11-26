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
app.secret_key = b'Secret!'

# The database URI should be in the format: postgresql://<db-user>:<pass>@<server-ip>/<db-name>
DB_USER = 'sy2751'
DB_PASSWORD = 'Secret!'
DB_SERVER = 'w4111.cisxo09blonu.us-east-1.rds.amazonaws.com'
DATABASE_URI = 'postgresql://' + DB_USER + ':' + DB_PASSWORD + '@' + DB_SERVER + '/w4111'

# Create an Engine object that connects to the DBAPI and the database.
engine = create_engine(DATABASE_URI)

# Create table test and insert values.
engine.execute("""DROP TABLE IF EXISTS test;""")
engine.execute("""
               CREATE TABLE IF NOT EXISTS test (
                   uid int,
                   username text,
                   PRIMARY KEY (uid)
               );
               """)
engine.execute("""INSERT INTO test(uid, username) VALUES
                  (0, 'stanley'), (1, 'yang'), (2, 'eugene');""")

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
        # Database query example.
        cursor = g.conn.execute("SELECT * FROM test")
        for result in cursor:
            print list(result)
        cursor.close()
        return render_template('login.html')
    else:
        return render_template('index.html')

# # Flask uses Jinja templates, which is an extension to HTML where you can
# # pass data to a template and dynamically generate HTML based on the data
# # (you can think of it as simple PHP)
# # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
# #
# # You can see an example template in templates/index.html
# # https://docs.sqlalchemy.org/en/latest/core/tutorial.html
#     context = dict(data = names)
#     return render_template('index.html', **context)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.form['password'] == 'password' and request.form['username'] == 'admin':
        session['logged_in'] = True
    else:
        flash('Wrong password!')
    return index()

@app.route("/logout")
def logout():
    session['logged_in'] = False
    return redirect('/')

# Example of adding new data to the database.
@app.route('/add', methods=['POST'])
def add():
  name = request.form['username']
  print name
  cmd = 'INSERT INTO test(uid, username) VALUES (4, :name1),';
  g.conn.execute(text(cmd), name1 = name);
  return redirect('/')

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
