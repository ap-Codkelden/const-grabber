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
		self.post_db = sqlite3.connect('posts.db')
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

	def showBlackList(self):
		self.cursor.execute("SELECT * FROM blacklist;")
		c = self.cursor.fetchall()
		print (c)
		if len(c) == 0:
			print("There are no blacklisted UIDs")
		else:
			for bl in self.cursor.fetchall():
				print(bl + '\n')

	def addUserToBL(self, uid):
		if self.checkIfUserinBL(uid) == 0:
			print("No user with thid UID, appending...")
			self.cursor.execute("INSERT INTO blacklist VALUES ({0});".format(uid))
			self.post_db.commit()
		else:
			print("User already in BL, skip.")


	def delUserFromBL(self, uid):
		if self.checkIfUserinBL(uid) == 0:
			print("No user with this UID, skip.")
		else:
			self.cursor.execute("DELETE from blacklist where uid={0};".format(uid))
			self.post_db.commit()
			print("Deleted!")


	def checkIfUserinBL(self, uid):
		self.cursor.execute("SELECT uid FROM blacklist WHERE uid={0};".format(uid))
		c = self.cursor.fetchone()
		if c == None:
			return 0 # not exist
		else:
			return 1 # already in BL

	def deleteBLRecords(self):
		self.cursor.execute("""DELETE from posts where uid in (SELECT uid FROM blacklist);""")
		self.post_db.commit()
		self.cursor.execute("""DELETE from comments where uid in (SELECT uid FROM blacklist);""")
		self.post_db.commit()
		self.packDB()


	def packDB(self):
		self.cursor.execute("""VACUUM""")