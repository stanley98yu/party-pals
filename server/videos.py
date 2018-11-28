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
from googleapiclient.discovery import build
from server import socketio, app, engine
import time
import datetime

CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
DEVELOPER_KEY = 'AIzaSyBHJuPLIexUXa6TJktAT_nXG_tS3LjuUeg'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'


@app.route('/party/<room>', defaults={'video': None})
@app.route('/party/<room>/<video>')
def party_room(room, video):
    if video is None:
        if not room or not session.get('logged_in'):
            return redirect('/')

        # Create a Youtube service object and request video search results by interest keywords.
        youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)
        resp = youtube.search().list(
            part='snippet',
            q="|".join(session['interests'].split(',')),
            maxResults=5
        ).execute()
        playlist = []
        for search_result in resp.get('items', []):
            # Checks the result is a video and not a playlist or live video.
            if search_result['id']['kind'] == 'youtube#video' and search_result['snippet']['liveBroadcastContent'] == 'none':
                playlist.append(search_result['id']['videoId'])

        # Reload if no videos were found, else makes currVideo the first video.
        if not playlist:
            return redirect('/')
        currVideo = playlist[0]

        stmt = text("""SELECT * FROM party_created
                        WHERE party_name=:party_name
                        ORDER BY pid DESC
                        LIMIT 1""")
        stmt = stmt.bindparams(bindparam("party_name", type_=String))
        cursor = g.conn.execute(stmt, {"party_name": room})

        rooms = cursor.fetchall()
        if len(rooms): # Party already exists with playlist.
            session['pid'] = rooms[0]['pid']
            # print("uid: " + str(session['uid']))
            # print("pid: " + str(session['pid']))
            join_time = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
            session['join_time'] = join_time
            # Insert into participates table.
	    stmt = text("""
                        INSERT INTO participates (uid, pid, join_time)
                        VALUES (:uid, :pid, to_timestamp(:join_time, 'YYYY-MM-DD hh24:mi:ss'))
                        """)
            stmt = stmt.bindparams(bindparam("uid", type_=Integer),\
                                   bindparam("pid", type_=Integer),\
                                   bindparam("join_time", type_=String))
            g.conn.execute(stmt, {"uid": session['uid'], "pid": session['pid'], "join_time": session['join_time']})
	    
            session['playlist'] = playlist
            session['room'] = room
            return redirect('/party/' + room + '/' + currVideo)
            # context = dict(room=room, playlist=json.dumps(playlist))
            # return render_template('party.html', **context)
        else: # Create new party.
            # Insert into party_created table.
            join_time = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
            session['join_time'] = join_time
            cursor = g.conn.execute("""SELECT pid FROM party_created ORDER BY pid DESC LIMIT 1""")
            next_id = cursor.fetchone()['pid'] + 1
            stmt = text("""
                        INSERT INTO party_created (uid, pid, party_name, creation_time)
                        VALUES (:uid, :pid, :room, to_timestamp(:creation_time, 'YYYY-MM-DD hh24:mi:ss'))
                        """)
            stmt = stmt.bindparams(bindparam("uid", type_=Integer),\
                                   bindparam("pid", type_=Integer),\
                                   bindparam("room", type_=String),\
                                   bindparam("creation_time", type_=String))
            g.conn.execute(stmt, {"uid": session['uid'], "pid": next_id, "room": room, "creation_time": session['join_time']})

	    # Insert into participates table.
	    stmt = text("""
                        INSERT INTO participates (uid, pid, join_time)
                        VALUES (:uid, :pid, to_timestamp(:join_time, 'YYYY-MM-DD hh24:mi:ss'))
                        """)
            stmt = stmt.bindparams(bindparam("uid", type_=Integer),\
                                   bindparam("pid", type_=Integer),\
                                   bindparam("join_time", type_=String))
            g.conn.execute(stmt, {"uid": session['uid'], "pid": session['pid'], "join_time": session['join_time']})
            # Insert into tags table.
	    for i in session['interests'].split(','):
                stmt = text("""
                            INSERT INTO tags (pid, keyword) VALUES
                            (:pid, :keyword) ON CONFLICT DO NOTHING;
                            """)
                stmt = stmt.bindparams(bindparam("pid", type_=Integer), \
                                       bindparam("keyword", type_=String))
                if re.match(r'\w+', i):
		    if len(i) > 20:
                        intrst = i[0:20]
                    else:
                        intrst = i
                    cursor = g.conn.execute(stmt, {"pid": next_id, "keyword": intrst})

            # Insert into playlist_generates table.
            cursor = g.conn.execute("""SELECT plid FROM playlist_generates ORDER BY plid DESC LIMIT 1""")
            next_id = cursor.fetchone()['plid'] + 1
            cursor.close()
            # Check interest exists.
            cursor = g.conn.execute("""SELECT keyword FROM interest
                                       WHERE keyword='%s'
                                       LIMIT 1""" % (session['interests'].split(',')[0]))
            res = cursor.fetchone()
            if not res:
                print "Can't find interest!"
                return redirect('/')
            else:
                key = res['keyword']
                g.conn.execute("""INSERT INTO playlist_generates(plid, keyword) VALUES
                                  (%d, '%s')""" % (next_id, key))

            # Get content details of each video ID and insert into database.
            content = youtube.videos().list(part='id,snippet,contentDetails', id=','.join(playlist)).execute()
            for result in content['items']:
                yid = result['id']
                title = result['snippet']['title']
                channel = result['snippet']['channelTitle']
                duration = re.findall(r'\d+', result['contentDetails']['duration'])
                length = format_duration(duration)

                stmt = text("""
                            INSERT INTO videos (vid,title,channel,length) VALUES
                            (:vid, :title, :channel, :length) ON CONFLICT DO NOTHING
                            """)
                stmt = stmt.bindparams(bindparam("vid", type_=String),\
                                       bindparam("title", type_=String),\
                                       bindparam("channel", type_=String),\
                                       bindparam("length", type_=String))
                g.conn.execute(stmt, {"vid": yid, "title": title, "channel": channel, "length": length})

            # Insert into playlist_contains table.
            for v in playlist:
                cursor = g.conn.execute("""INSERT INTO playlist_contains (plid,vid,user_votes) VALUES
                                           (%d, '%s', %d)"""
                                           % (next_id, v, 0))

            # Clean up and start party webpage request.
            cursor.close()
            session['playlist'] = playlist
            session['currVideo'] = currVideo
            session['room'] = room
            return redirect('/party/' + room + '/' + currVideo)
    else:
        # Insert into video_plays table.
        cursor = g.conn.execute("""SELECT pid FROM party_created
                                   WHERE party_name='%s' LIMIT 1""" % (room))
        pid = cursor.fetchone()['pid']
        stmt = text("""
                    INSERT INTO video_plays (pid,vid,start_time) VALUES
                    (:pid, :vid, to_timestamp(:start_time, 'YYYY-MM-DD hh24:mi:ss')) ON CONFLICT DO NOTHING
                    """)
        stmt = stmt.bindparams(bindparam("pid", type_=Integer),\
                               bindparam("vid", type_=String),\
                               bindparam("start_time", type_=String))
        g.conn.execute(stmt, {"pid": pid, "vid": video, "start_time": session['join_time']})

        context = dict(room=room, playlist=json.dumps(session['playlist']), currVideo=video)
        return render_template('party.html', **context)

@socketio.on('syncvideo', namespace='/party')
def sync(msg):
    """Syncs up video players within the same room."""
    emit('update-vid', msg, room=msg['room'])

@socketio.on('vote', namespace='/party')
def vote(msg):
    """Tally votes for a specific video."""
    print 'Vote!'
    # g.conn.execute("""
    #            UPDATE playlist_contains
    #            SET user_votes = user_votes + 1
    #            WHERE plid=%d AND vid='%s'
    #            """ % (msg['plid'], msg['vid']))

def format_duration(duration):
    """Format duration into interval format."""
    if len(duration) == 1:
        return '0:0:' + duration[0]
    elif len(duration) == 2:
        return '0:' + duration[0] + ':' + duration[1]
    else:
        return ':'.join(duration)
