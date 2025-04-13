CREATE TABLE IF NOT EXISTS news
(post_id INTEGER PRIMARY KEY AUTOINCREMENT,
text TEXT,
dt DATE,
img BLOB DEFAULT NULL);

CREATE TABLE IF NOT EXISTS pictures
(pic_id INTEGER PRIMARY KEY AUTOINCREMENT,
text TEXT,
dt DATE,
img BLOB DEFAULT NULL);

CREATE TABLE IF NOT EXISTS siteinfo
(photo BLOB DEFAULT NULL);,
description TEXT,
email TEXT,
phone TEXT);

CREATE TABLE IF NOT EXISTS users
(user_id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT NOT NULL,
psw TEXT NOT NULL);

INSERT INTO users VALUES (1, 'admin', 'afdd0b4ad2ec172c586e2150770fbf9e');
