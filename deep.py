#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import sqlite3
import urllib.request
import json
import sys
from db_handle import db_handle

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('-v', '--verbose', help='print messages', \
                        action='store_true', default=False, dest='verbose')


THREAD_URL="""http://api.juick.com/thread?mid="""
URL_STRING = """http://api.juick.com/messages?tag=%D1%81%D0%BE%D0%B7%D0%B2%D0%B5%D0%B7%D0%B4%D0%B8%D0%B5&page="""

post_db = sqlite3.connect('posts.db')
cursor = post_db.cursor()

live_db = sqlite3.connect(':memory:')
c_live = live_db.cursor()

c_live.execute("create table stored_posts (mid integer)")
c_live.execute("create table exist_posts (mid integer)")


def compareAndAdd(mid, exist_mid_replies, stored_mid_replies):
	content = GetContent(mid, THREAD_URL)
	for x in range(stored_mid_replies+1,exist_mid_replies+1):
		cursor.execute("INSERT INTO comments VALUES ({0},{1},{2},{3},'{4}','{5}','{6}')".format(content[x]['mid'],content[x]['rid'],\
			(content[x]['replyto'] if 'replyto' in content[x] else 'null'), \
			content[x]['user']['uid'],content[x]['user']['uname'],content[x]['body'],\
			content[x]['timestamp']))

def comment_deep_scan():
	print("Start...")
	"""Вернет список вида
	[(12345, 0), (mid, replies count)]"""
	cursor.execute("select p.mid, count(c.rid) from posts p left outer join comments c on  p.mid = c.mid group by p.mid")
	stored_posts_replies_count = cursor.fetchall()
	"""Запуск выборки количества комментариев на текущий момент по сохраненным номерам
	постов, для чего вызывается фнукция get_live_replies_count() с аргументом
	stored_posts_replies_count , из которого она возьмет номера"""
	live_posts_replies_count = get_live_replies_count(stored_posts_replies_count)
	for i in range(len(live_posts_replies_count)):
		if live_posts_replies_count[i] != stored_posts_replies_count[i]:
			print(stored_posts_replies_count[i],'=>',live_posts_replies_count[i])
			"""Функция compareAndAdd принимает аргументы:
			Номер сообщения, Число комментариев в жуйке,
			Число комментариев в базе"""
			compareAndAdd(live_posts_replies_count[i][0], live_posts_replies_count[i][1], \
				stored_posts_replies_count[i][1])


def get_live_replies_count(saved_posts):
	""" saved_posts -- список котрежей, содержащих номера
	постов
	возвратит количество комментариев у сообщения #12345 """
	counter = 0
	live_replies = []
	for i in saved_posts:
		counter += 1
		if counter % 10 == 0:
			print(counter)
		thread = urllib.request.urlopen(THREAD_URL+str(i[0]))
		thread = thread.read().replace(b"\t", b"").replace(b"'",b"''")
		thread = thread.decode('utf-8')
		thread = json.loads(thread)
		if len(thread) > 1:
			live_replies.append((i[0],len(thread)-1))
		else:
			live_replies.append((i[0],0))
	return live_replies


def GetContent(number, url=URL_STRING):
	try:
		text = urllib.request.urlopen(url + str(number))
		raw_content = text.read().replace(b"\t", b"")
		readable = raw_content.decode('utf-8')
		json_data = json.loads(readable)
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
	"""TODO
	избавиться от переменных"""
	POST_URL = """http://api.juick.com/thread?mid="""
	for lost in lost_posts:
		text = urllib.request.urlopen(POST_URL + str(lost[0]))
		raw_content = text.read().replace(b"\t", b"")
		readable = raw_content.decode('utf-8')
		post = json.loads(readable)[0]
		sql = """INSERT INTO posts VALUES (%d, %d, "%s", "%s", "%s", "%s", %d)""" % \
		(post['mid'], post['user']['uid'], post['user']['uname'], post['body'], \
			post['tags'], post['timestamp'], (post['replies'] if 'replies' in post else 0))
		cursor.execute(sql)
		post_db.commit()

def get_juick_posts(page_number):
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

def pack():
	cursor.close()
	post_db.close()
	db = db_handle()
	# delete records from BL
	db.deleteBLRecords()
	if args.verbose:
		db.cursor.execute("SELECT COUNT(*) from posts")
		count_posts=db.cursor.fetchone()[0]

		db.cursor.execute("SELECT COUNT(*) from comments")
		count_replies=db.cursor.fetchone()[0]

		sys.stdout.write("There are {0} messages, {1} comments in database.\n".format(count_posts,count_replies))

if __name__ == "__main__":
	args = arg_parser.parse_args()
	number = 1
	get_stored_posts()
	get_juick_posts(number)
	c_live.execute("select count(mid) from exist_posts")
	print(c_live.fetchone())
	append(seek_difference())

	comment_deep_scan()
	# temporary until this module will be use DBHandle
	pack()



