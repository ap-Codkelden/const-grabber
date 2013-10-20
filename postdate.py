#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Количество постов по датам
"""

import sqlite3
import csv
from db_handle import db_handle

def get_posts():
	db = db_handle()
	db.cursor.execute("SELECT uid, substr(timestamp,1,4), substr(timestamp,6,2) FROM posts;")
	posts = db.cursor.fetchall()
	return posts

def get_names():
	db = db_handle()
	db.cursor.execute("SELECT DISTINCT uid, uname FROM posts ORDER BY uid;")
	names = db.cursor.fetchall()
	return names

def write_csv(rows):
	with open('poststat.csv', 'w', newline='') as csvfile:
		spamwriter = csv.writer(csvfile,delimiter=';')
		spamwriter.writerow(['uname', 'posts_count', 'month', 'year'])
		for r in rows:
			spamwriter.writerow(r)


if __name__ == "__main__":
	mb = sqlite3.connect(':memory:')
	c = mb.cursor()
	c.execute("create table users (\
		uid integer primary key, \
		uname text);")

	c.execute("create table posts (uid integer, year integer, month integer, count integer, \
		FOREIGN KEY(uid) REFERENCES users(uid));")
	mb.commit()

	names = get_names()
	posts = get_posts()

	for i in names:
		c.execute("INSERT INTO users VALUES (?, ?);", (i))
	for i in posts:
		k = [f for f in i]
		k.append(1)
		c.execute("INSERT INTO posts VALUES (?, ?, ?, ?);", (k))

	write_csv(c.execute("SELECT '@'||users.uname, sum(posts.count),  posts.month, posts.year  FROM posts join users on posts.uid = users.uid group by 1,3,4;"))