#!/usr/bin/env python2.7
"""Manages interactions with videos using the Youtube Data API."""

import os
import re
import json
import datetime
import time
from flask import Flask, render_template, redirect, url_for, session, request, g
from flask_socketio import emit
from sqlalchemy import *
from sqlalchemy.pool import NullPool
import google_auth_oauthlib.flow
import google.oauth2.credentials
from googleapiclient.discovery import build
from server import socketio, app, engine
import time
import datetime

CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
DEVELOPER_KEY = 'secret'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

@app.route('/party/<room>')
def party_room(room):
    if not room or not session.get('logged_in'):
        return redirect('/')

    # # Load the credentials from the session.
    # credentials = google.oauth2.credentials.Credentials(
    #     **session['credentials'])
    stmt = text("""SELECT * FROM test2
                    WHERE party_name=:party_name
                    ORDER BY pid DESC
                    LIMIT 1""")
    stmt = stmt.bindparams(bindparam("party_name", type_=String))
    cursor = g.conn.execute(stmt, {"party_name": room})
    if len(cursor.fetchall()):
        for result in cursor:
            pid = result['pid']
            session['pid'] = pid
        print("uid: " + str(session['uid']))
        print("pid: " + str(session['pid']))
        join_time = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
        session['join_time'] = join_time
        stmt = text("""
                    INSERT INTO test_participate (uid, pid, join_time)
                    VALUES (:uid, :pid, to_timestamp(:join_time, 'YYYY-MM-DD hh24:mi:ss'))
                    """)
        stmt = stmt.bindparams(bindparam("uid", type_=Integer),\
                               bindparam("pid", type_=Integer),\
                               bindparam("join_time", type_=String))
        g.conn.execute(stmt, {"uid": session['uid'], "pid": session['pid'], "join_time": session['join_time']})
        context = dict(room=room, playlist=json.dumps([]), host=0)
        return render_template('party.html', **context)
    else:
        # Create a Youtube service object and request video search results by interest keywords.
        youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)
        resp = youtube.search().list(
            part='snippet',
            q="|".join(session['interests'].split(',')),
            maxResults=1
        ).execute()
        playlist = set()
        for search_result in resp.get('items', []):
            # Checks the result is a video and not a playlist or live video.
            if search_result['id']['kind'] == 'youtube#video' and search_result['snippet']['liveBroadcastContent'] == 'none':
                playlist.add(search_result['id']['videoId'])
        
        # Get content details of each video ID and insert into database.
        content = youtube.videos().list(part='id,snippet,contentDetails', id=','.join(playlist)).execute()
        for result in content['items']:
            yid = result['id']
            title = result['snippet']['title']
            channel = result['snippet']['channelTitle']
            duration = re.findall(r'\d+', result['contentDetails']['duration'])
            length = format_duration(duration)

            cursor = g.conn.execute("""INSERT INTO videos (vid,title,channel,length) VALUES
                                       ('%s', '%s', '%s', '%s') ON CONFLICT DO NOTHING"""
                                       % (yid, title, channel, length))

        # Return user to homepage if no results found using interests listed.
        context = dict(room=room, playlist=json.dumps(list(playlist)), host=1)
        if playlist:
            cursor.close()
            return render_template('party.html', **context)
        else:
            cursor.close()
            return redirect('/')

@socketio.on('syncvideo', namespace='/party')
def sync(msg):
    """Syncs up video players within the same room."""
    emit('update-vid', msg, room=msg['room'])

@socketio.on('vote', namespace='/party')
def vote(msg):
    """Tally votes for a specific video."""
    print 'Voted!'

def format_duration(duration):
    """Format duration into interval format."""
    if len(duration) == 1:
        return '0:0:' + duration[0]
    elif len(duration) == 2:
        return '0:' + duration[0] + ':' + duration[1]
    else:
        return ':'.join(duration)

@app.route('/authorize')
def authorize():
    # Create a flow instance to manage the OAuth 2.0 Authorization Grant Flow
    # steps.
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES)
    flow.redirect_uri = url_for('oauth2callback', _external=True)
    authorization_url, state = flow.authorization_url(
      # This parameter enables offline access which gives your application
      # both an access and refresh token.
      access_type='offline',
      # This parameter enables incremental auth.
      include_granted_scopes='true')
    # Store the state in the session so that the callback can verify that
    # the authorization server response.
    session['state'] = state
    return redirect(authorization_url)

@app.route('/oauth2callback')
def oauth2callback():
    # Specify the state when creating the flow in the callback so that it can
    # verify the authorization server response.
    state = session['state']
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = url_for('oauth2callback', _external=True)
    
    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)

  # Store the credentials in the session.
  # ACTION ITEM for developers:
  #     Store user's access and refresh tokens in your data store if
  #     incorporating this code into your real app.
    credentials = flow.credentials
    session['credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }
    return redirect(url_for('index'))
