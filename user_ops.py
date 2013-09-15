#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
User operational module.
Contain procedures:
	create_user_list()
	delete_user_list()
for creating and deleting 
table USERS in the POSTS database according.
"""

import sqlite3

class db_handle:

	def __init__(self):
		self.create_connection()

	def create_connection(self):
		self.post_db = sqlite3.connect('post.db')
		self.cursor = self.post_db.cursor()


	def create_user_list(self):
		self.cursor.execute("CREATE TABLE IF NOT EXISTS users (uid integer, uname text);")
		self.post_db.commit()
		self.cursor.execute("SELECT DISTINCT uid, uname FROM posts;")
		users = self.cursor.fetchall()
		for i in users:
			self.cursor.execute("INSERT INTO users VALUES (%d, '%s')" % (i[0], i[1]))

	def delete_user_list(self):
		self.post_db.commit
		self.cursor.execute("DROP TABLE users")
		self.post_db.commit