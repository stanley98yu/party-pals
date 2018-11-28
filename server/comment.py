#!/usr/bin/env python2.7
"""Handles real-time, interactive comment system."""


#from flask import Flask, request, render_template, g, redirect, Response, session, flash
#from flask_socketio import join_room, leave_room, emit
#from server import socketio, engine, app
#import time
#import datetime
from sqlalchemy import *
from sqlalchemy.pool import NullPool

import os
import json
from flask import Flask, render_template, redirect, url_for, session, request, g
from flask_socketio import emit, join_room, leave_room
import google_auth_oauthlib.flow
import google.oauth2.credentials
from googleapiclient.discovery import build
from server import socketio, app, engine
import time
import datetime

@socketio.on('joined', namespace='/party')
def joined(message):
    """Broadcast to all in room after joining."""
    room = session.get('room')
    join_room(room)
    emit('status', {'msg': session.get('username') + ' has entered the room.'}, room=room)

@socketio.on('comment', namespace='/party')
def comment(message):
    """Writing a comment."""
    room = session.get('room')
    emit('message', {'username': session.get('username'), 'msg': message['msg']}, room=room)

@socketio.on('left', namespace='/party')
def left(message):
    """Broadcast to all in room after leaving."""
    room = session.get('room')
    emit('status', {'msg': session.get('username') + ' has left the room.'}, room=room)
