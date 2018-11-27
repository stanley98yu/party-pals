#!/usr/bin/env python2.7
"""Runner for the Flask application."""

import os
import click
from server import socketio, app

if __name__ == '__main__':
    # Handles command line interface.
    @click.command()
    @click.option('--debug', is_flag=True)
    @click.argument('host', default='0.0.0.0')
    @click.argument('port', default=8111, type=int)

    def run(host, port, debug):
        print "Running on %s:%d" % (host, port)
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
        socketio.run(app, host=host, port=port, debug=debug)

    run()