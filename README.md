COMS 4111 Project 1
===================

VideoParty is a recommendation and media-sharing application that allows users to form groups, also known as parties, to watch videos together. Users can share Youtube videos within parties, watch them together, and vote for what kinds of videos they want to share with others. The application's main entities would be **users**, **parties**, **sessions**, and **videos**. Users join parties that have similar interests. For instance, users could be part of a "Hip Hop Music" party, and the app will recommend videos by pulling data from the Youtube (or Spotify for music) API with _tags_ that relate to hip hop. Users could then **participate** in a session that **displays** a video or playlist of videos. Data collected from user votes and views will be pushed to the database to influence future video recommendations in the party or other parties with related interests. Sessions must be constrained to _need at least one participant_, and a session can only play _exactly one video at a time_. During sessions, users can also write **comments** that is uniquely identified by the video it belongs to and its comment ID. Each session, a user must be either a **moderator** or a **spectator**, though a session must have _exactly one moderator_. Although the moderator gets to choose which video to watch in the session, spectators get to add videos they would like to see on a **watch list**, which is appended to the **recommendation list** that the app suggests for the party.

Created by Yang He and Stanley Yu. Made for COMS 4111 (Fall '18).

## Contingency Plan

The contingency plan simplifies the VideoParty platform to only involve **users**, **sessions**, and **videos**, removing the group dynamic. Instead, users will simply join or create sessions that are associated with _tags_. To simplify the democratic process within a session, each user will _like or dislike_ the video played during the session and vote for which video they want to see next. As before, sessions **display** videos that users **participating** in that session can also make **comments** on. A session will contain a **watch list** that lists the videos that the app recommends and users **suggest**.
