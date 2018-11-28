Project 1 Part 3
================

* Stanley Yu (sy2751)
* Yang He (yh2825)
* Link to Github repo: https://github.com/stanley98yu/party-pals
* Application URL: http://35.237.70.91:8111

## Changes Made To Schema since Part 2

* Added 'password' column to 'users' table for new login functionality.
* Changed 'songs' entity to 'videos' entity since we decided to use the Youtube API rather than Spotify because Spotify's restrictions on accounts created too many restrictions on the app (such as needing to have an email associated with a Spotify Premium account). Mostly everything is the same except sid is replaced by vid, which is a unique ID provided by Youtube for each video. This change propagated to song_plays, which was changed to video_plays and comment_belongs_to, which now has a vid column, and playlist_contains, which also has a vid column. However, the functionality of the tables is still the same.
* Removed end_time from video_plays and participates because Socket.IO does not fire its disconnect event for all types of disconnections, such as exiting the browser window, on all browsers (this was not working on Firefox). Thus, it was not viable to consistently record the end_time for every user and play session.
* Changed primary key of interest table to keyword to avoid duplicates of keywords building up. This changed the foreign key for the tags and playlist_generates 
* The comment_belongs_to table is not recorded correctly. This is because of the way Flask global context works: we can't access the database engine directly from a Flask SocketIO event, which is how each comment is propagated to all users in the room and back to the Flask server.