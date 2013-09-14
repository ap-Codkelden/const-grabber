#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import urllib.request
import json
import sqlite3
from operator import itemgetter
import http.client
import sys 

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('-v', '--verbose', help='print messages', \
                        action='store_true', default=False, dest='verbose')

URL_STRING = """http://api.juick.com/messages?tag=%D1%81%D0%BE%D0%B7%D0%B2%D0%B5%D0%B7%D0%B4%D0%B8%D0%B5&page="""

def create_db():
	global cursor
	global post_db
	post_db = sqlite3.connect('post.db')
	cursor = post_db.cursor()

	cursor.execute('''CREATE TABLE if not exists posts (msgid integer, uid integer, uname text, body text, tags text, timestamp text, replies integer)''')
	post_db.commit()


def GetContent(number, url=URL_STRING):
	try:
		text = urllib.request.urlopen(url + str(number))
		if args.verbose:
			sys.stdout.write("Retrieve page %d...\n"  % number)
		raw_content = text.read().replace(b"\t", b"")
		readable = raw_content.decode('utf-8')
		json_data = json.loads(readable)
		return json_data
	except urllib.error.HTTPError:
		return 0


def json_parser(posts):
	for post in posts:
		msgid = post['mid']
		uid = post['user']['uid']
		uname = post['user']['uname']
		body = post['body']
		tags = post['tags']
		timestamp = post['timestamp']
		try:
			replies = post['replies']
		except KeyError:
			replies = 0
		if msgid == last_post:
			if args.verbose:
				sys.stdout.write("There are no new messages, stop fetching...\n\n")
			return 0
		else:
			sql = """INSERT INTO posts VALUES (%d, %d, "%s", "%s", "%s", "%s", %d)""" % \
			(msgid, uid, uname, body, tags, timestamp, replies)
			cursor.execute(sql)
			post_db.commit()
	return 1


def GetLastPost():
	cursor.execute("SELECT COUNT(*) from posts")
	result=cursor.fetchone()
	if result[0] == 0:
		return 0
	else:
		cursor.execute("SELECT max(msgid) from posts")
		result=cursor.fetchone()
		return result[0]


def get_comments():
	pass


def main():
	page_number = 1
	try:
		create_db()
	except:
		sys.stdout.write("Error database creation.\n")

	global last_post
	last_post = GetLastPost()
	if args.verbose:
		if last_post == 0:
			sys.stdout.write("We are have no data about the number\nof the last post, is this 1st run?\n")
		else:
			sys.stdout.write("Last message is message #{0}\n".format(last_post))

	#while page_number < 5:
	while True:
		data = GetContent(page_number)
		if data != 0:
			if json_parser(data) == 1:
				page_number += 1
			else:
				break
		else:
			break
	
	if args.verbose:
		cursor.execute("SELECT COUNT(*) from posts")
		result=cursor.fetchone()[0]
		pages = page_number-1
		sys.stdout.write("There are {0} messages in database.\n".format(result))


if __name__ == "__main__":
	args = arg_parser.parse_args()
	main()