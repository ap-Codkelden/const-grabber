#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
import urllib.request
import json
import sys

URL_STRING = """http://api.juick.com/messages?tag=%D1%81%D0%BE%D0%B7%D0%B2%D0%B5%D0%B7%D0%B4%D0%B8%D0%B5&page="""


post_db = sqlite3.connect('post.db')
cursor = post_db.cursor()

live_db = sqlite3.connect(':memory:')
c_live = live_db.cursor()

c_live.execute("create table stored_posts (mid integer)")
c_live.execute("create table exist_posts (mid integer)")


def GetContent(number, url=URL_STRING):
	try:
		text = urllib.request.urlopen(url + str(number))
		raw_content = text.read().replace(b"\t", b"")
		readable = raw_content.decode('utf-8')
		json_data = json.loads(readable)
		#print(json_data)
		return json_data
	except urllib.error.HTTPError:
		#sys.stdout.write("Total pages count: %d\n" % number-1)
		return



def get_stored_posts():
	cursor.execute("SELECT mid FROM posts;")
	for x in cursor.fetchall():
		c_live.execute("insert into stored_posts values (%d)" % x[0])

	c_live.execute("select count(mid) from stored_posts")
	for i in c_live.fetchall():
		print(i)

def data_parse(json_data):
	for post in json_data:
		message_id = post['mid']
		c_live.execute("insert into exist_posts values (%d)" % message_id)


def seek_difference():
	c_live.execute("select e.mid from exist_posts e left outer join stored_posts s on e.mid = s.mid where s.mid is null")
	return c_live.fetchall()

def append(lost_posts):
	POST_URL = """http://api.juick.com/thread?mid="""
	for lost in lost_posts:
		#print(POST + str(lost))
		text = urllib.request.urlopen(POST_URL + str(lost[0]))
		raw_content = text.read().replace(b"\t", b"")
		readable = raw_content.decode('utf-8')
		post = json.loads(readable)[0]
		#print(json_data)
		mid = post['mid']
		uid = post['user']['uid']
		uname = post['user']['uname']
		body = post['body']
		tags = post['tags']
		timestamp = post['timestamp']
		try:
			replies = post['replies']
		except KeyError:
			replies = 0
		#print(mid,'\t',last_post)
		sql = """INSERT INTO posts VALUES (%d, %d, "%s", "%s", "%s", "%s", %d)""" % \
		(mid, uid, uname, body, tags, timestamp, replies)
		print(sql)
		cursor.execute(sql)
		post_db.commit()




def get_juick_posts(page_number):
	#while page_number < 77:
	while True:
		try:
			print(page_number)
			data = GetContent(page_number)
			if data != None:
				data_parse(data)
				page_number += 1
			else:
				break
		except (urllib.error.HTTPError):
			sys.stdout.write("Total pages count: %d\n" % page_number-1)
			break


if __name__ == "__main__":
	number = 1
	get_stored_posts()
	get_juick_posts(number)
	c_live.execute("select count(mid) from exist_posts")
	print(c_live.fetchone())
	append(seek_difference())