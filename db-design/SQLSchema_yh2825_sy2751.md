SQL Schema for MusicParty
=========================

```sql
CREATE TABLE User(
	uid int,
	username char(20) NOT NULL,
	date_of_birth date NOT NULL,
	email text NOT NULL,
	PRIMARY KEY (uid)
)

CREATE TABLE Party(
	pid int,
	party_name text,
	creation_time timestamp,
	uid int NOT NULL,
	PRIMARY KEY (pid),
	FOREIGN KEY (uid) REFERENCES User
		ON DELETE NO ACTION
)

CREATE TABLE Participates(
	uid int,
	pid int,
	join_time timestamp,
	end_time timestamp,
	PRIMARY KEY (uid, pid)
	FOREIGN KEY (uid) REFERENCES User,
	FOREIGN KEY (pid) REFERENCES Party
)

CREATE TABLE Song(
	sid int,
	title text NOT NULL,
	length int NOT NULL,
	PRIMARY KEY (sid)
)

CREATE TABLE Song_Plays(
	pid int,
	sid int,
	start_time timestamp,
	end_time timestamp,
	PRIMARY KEY (pid, sid),
	FOREIGN KEY (pid) REFERENCES Party,
	FOREIGN KEY (sid) REFERENCES Song
)

CREATE TABLE Comment_Belongs_To(
	cid int,
	message text,
	creation_time timestamp,
	uid int,
	pid int,
	sid int,
	PRIMARY KEY (cid, uid, pid, sid),
	FOREIGN KEY (pid, sid) REFERENCES Song_Plays
		ON DELETE CASCADE,
	FOREIGN KEY (uid) REFERENCES User
		ON DELETE CASCADE
)

CREATE TABLE Interest(
	interest_id int,
	category text,
	keyword char(20),
	PRIMARY KEY (interest_id)
)

CREATE TABLE Tags(
	interest_id int,
	pid int,
	PRIMARY KEY (interest_id, pid),
	FOREIGN KEY (interest_id) REFERENCES Interest,
	FOREIGN KEY (pid) REFERENCES Party
)

CREATE TABLE Playlist_Generates(
	plid int,
	interest_id int,
	PRIMARY KEY (plid),
	FOREIGN KEY (interest_id) REFERENCES Interest
)

CREATE TABLE Contains(
	plid int,
	sid int NOT NULL,
	user_votes int,
	PRIMARY KEY (plid, sid)
	FOREIGN KEY (plid) REFERENCES Playlist,
	FOREIGN KEY (sid) REFERENCES Song
)
```

