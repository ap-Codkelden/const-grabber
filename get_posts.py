#!/usr/bin/env python3
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

arg_parser.add_argument('-l', '--logging', help='write errors log', \
                        action='store_true', default=False, dest='log')

URL_STRING = """http://api.juick.com/messages?tag=%D1%81%D0%BE%D0%B7%D0%B2%D0%B5%D0%B7%D0%B4%D0%B8%D0%B5&page="""
URL_COMMENT = """http://api.juick.com/thread?mid="""

def create_db():
	global cursor
	global post_db
	post_db = sqlite3.connect('posts.db')
	cursor = post_db.cursor()

	cursor.execute('''CREATE TABLE if not exists posts (mid integer, uid integer, uname text, body text, \
		tags text, timestamp text, replies integer)''')
	cursor.execute("""CREATE TABLE if not exists comments (mid integer, rid integer, replyto integer, \
		uid integer, uname text, body text, timestamp text)""")
	post_db.commit()


def GetContent(number, url=URL_STRING):
	try:
		text = urllib.request.urlopen(url + str(number))
		if args.verbose:
			sys.stdout.write("Retrieve page %d...\n"  % number)
		raw_content = text.read().replace(b"\t", b"")
		readable = raw_content.replace(b"'",b"''").decode('utf-8')
		json_data = json.loads(readable)
		return json_data
	except urllib.error.HTTPError:
		return 0


def json_parser(posts):
	for post in posts:
		if post['mid'] == last_post:
			if args.verbose:
				sys.stdout.write("There are no new messages, stop fetching...\n\n")
			return 0
		else:
			sql = """INSERT INTO posts VALUES ({0}, {1}, '{2}', "{3}", "{4}",\
				"{5}", {6})""".format(post['mid'], post['user']['uid'],\
				post['user']['uname'], post['body'], post['tags'], post['timestamp'],\
				(post['replies'] if 'replies' in post else 0))
			cursor.execute(sql)
			post_db.commit()
			new_posts.append(post['mid'])
	return 1


def GetLastPost():
	cursor.execute("SELECT COUNT(*) from posts")
	result=cursor.fetchone()
	if result[0] == 0:
		return 0
	else:
		cursor.execute("SELECT max(mid) from posts")
		result=cursor.fetchone()
		return result[0]


def fetch_comment(comment):
	try:
		post = urllib.request.urlopen(URL_COMMENT + str(comment))
		if args.verbose:
			sys.stdout.write("Retrieve comments to #{0}...\n".format(comment))
		post_raw_content = post.read().replace(b"\t", b"")
		post_content = post_raw_content.decode('utf-8')
		json_thread = json.loads(post_content)
		if len(json_thread) > 1:
			for c in range(0, len(json_thread)):
				mid = json_thread[c]['mid']
				if 'rid' in  json_thread[c]:
					rid = json_thread[c]['rid']
				else:
					rid = 'null'
				if 'replyto' in  json_thread[c]:
					replyto = json_thread[c]['replyto']
				else:
					replyto = 'null'
				uid = json_thread[c]['user']['uid']
				uname = json_thread[c]['user']['uname']
				body = json_thread[c]['body'].replace("'","''")
				timestamp = json_thread[c]['timestamp']
				cursor.execute("INSERT INTO comments VALUES ({0},{1},{2},{3},'{4}','{5}','{6}')".format(mid, rid, replyto, uid, uname, body, timestamp))
				post_db.commit()
		else:
			if args.verbose:
				sys.stdout.write("Message #{0} have no replies, next...\n".format(comment))
			return 0
	except:
		e = sys.exc_info()[0]
		sys.stdout.write("Comments to message #{0} fetching error due to {1}.\n".format(comment, e))
		if args.log:
			logfile.write("\nErr_msg: {0}\n".format(e))
			logfile.write("INSERT INTO comments VALUES ({0},{1},{2},{3},'{4}','{5}','{6}')".format(mid, rid, replyto, uid, uname, body, timestamp))
		pass


def get_comments():
	comm_dump = cursor.execute("SELECT DISTINCT mid from posts WHERE replies>0 and mid>{0}".format(last_post))
	comments = comm_dump.fetchall()
	for comment in comments:
		fetch_comment(comment[0])


def main():
	""" 	For production launch purposes, page_number variable always
	MUST be equal 1, but for debugging you can make it equal any
	non-negative integer lower than pages count 	"""
	page_number = 1

	""" 	new_posts -- this is a list in which will store numbers
	of the new discovering messages 	"""
	global new_posts
	new_posts = []

	try:
		create_db()
	except:
		sys.stdout.write("Error database creation.\n")

	global last_post
	last_post = GetLastPost()
	if args.verbose:
		if last_post == 0:
			sys.stdout.write("We have no data about the number\nof the last post, is this 1st run?\n")
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

	# We get the rockets, if its here :)
	if len(new_posts) > 0:
		get_comments()

	if args.verbose:
		cursor.execute("SELECT COUNT(*) from posts")
		count_posts=cursor.fetchone()[0]

		cursor.execute("SELECT COUNT(*) from comments")
		count_replies=cursor.fetchone()[0]

		sys.stdout.write("There are {0} messages, {1} comments in database.\n".format(count_posts,count_replies))


if __name__ == "__main__":
	args = arg_parser.parse_args()
	if args.log:
		#global logfile
		logfile = open('error.log', 'w')
	main()
	if args.log:
		logfile.close()
	exit(0)
