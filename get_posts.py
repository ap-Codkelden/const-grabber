#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import urllib.request
import json
import sqlite3
from operator import itemgetter
import sys 
import os


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
	#cursor.execute('''PRAGMA table_info(posts);''')
	#result=cursor.fetchall()
	#print(result)

def GetContent(number, url=URL_STRING):
	try:
		text = urllib.request.urlopen(url + str(number))
		if args.verbose:
			sys.stdout.write("Retrieve page %d...\n"  % number)
		raw_content = text.read().replace(b"\t", b"")
		readable = raw_content.decode('utf-8')
		json_data = json.loads(readable)
		#print(json_data)
		return json_data
	except urllib.error.HTTPError:
		#sys.stdout.write("Total pages count: %d\n" % number-1)
		return

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
		#print(msgid,'\t',last_post)
		if msgid == last_post:
			if args.verbose:
				sys.stdout.write("No new posts found in further, stop fetching...\n\n")
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

def create_user_list():
	cursor.execute("CREATE TABLE IF NOT EXISTS users (uid integer, uname text);")
	post_db.commit()
	cursor.execute("SELECT DISTINCT uid, uname FROM posts;")
	users = cursor.fetchall()
	for i in users:
		cursor.execute("INSERT INTO users VALUES (%d, '%s')" % (i[0], i[1]))

def delete_user_list():
	post_db.commit
	cursor.execute("DROP TABLE users")
	post_db.commit


def posts_per_user():
	create_user_list()
	cursor.execute("SELECT u.uname, COUNT(p.msgid)  FROM users u \
		LEFT OUTER JOIN posts p \
		ON u.uid = p.uid \
		GROUP BY u.uid, u.uname \
		ORDER BY 2 DESC")
	ppu = cursor.fetchall()
	delete_user_list()

	with open("posts_per_user.json", 'w') as ppu_file:
		json.dump(ppu, ppu_file,  ensure_ascii=False)
	sys.stdout.write('Data saved in posts_per_user.json\n')

def get_comments():
	pass


def main():
	page_number = 1
	try:
		create_db()
	except:
		sys.stdout.write("Error\n")

	global last_post
	last_post = GetLastPost()
	if args.verbose:
		if last_post == 0:
			sys.stdout.write("We are have no data about the number\nof the last post, is this 1st run?\n")
		else:
			sys.stdout.write("Last post is post #%d\n" % last_post)

	#while page_number < 5:
	while True:
		try:
			data = GetContent(page_number)
			if data != None:
				if json_parser(data) == 1:
					page_number += 1
				else:
					break
			else:
				break
		except (urllib.error.HTTPError):
			sys.stdout.write("Total pages count: %d\n" % page_number-1)
			break



	""" Вызов функций, представляющих всякую статистику """
	posts_per_user()

	
	if args.verbose:
		cursor.execute("SELECT COUNT(*) from posts")
		result=cursor.fetchone()
		sys.stdout.write("There are %d posts in database.\n" % result)


if __name__ == "__main__":
	# получаем агрументы командной строки
	args = arg_parser.parse_args()
	main()
	#make_total()