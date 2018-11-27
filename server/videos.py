#!/usr/bin/env python2.7
"""Manages interactions with videos using the Youtube Data API."""

import os
import json
from flask import Flask, render_template, redirect, url_for, session, request
import google_auth_oauthlib.flow
import google.oauth2.credentials
from googleapiclient.discovery import build
from server import socketio, app

CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
DEVELOPER_KEY = 'secret'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

@app.route('/party/<room>')
def party_room(room):
    if not room:
        return redirect('/')

    # # Load the credentials from the session.
    # credentials = google.oauth2.credentials.Credentials(
    #     **session['credentials'])
    # Example of a Youtube search result.
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)
    resp = youtube.search().list(
        part='snippet',
        q=str(session['interests']),
        maxResults=5
    ).execute()
    playlist = []
    for search_result in resp.get('items', []):
        playlist.append(search_result['id']['videoId'])
    print playlist
    return render_template('party.html', room=room, playlist=json.dumps(playlist))

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
