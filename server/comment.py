#!/usr/bin/env python2.7
"""Handles real-time, interactive comment system."""

from flask import Flask, session
from flask_socketio import join_room, leave_room, emit
from server import socketio

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
    leave_room(room)
    emit('status', {'msg': session.get('username') + ' has left the room.'}, room=room)
