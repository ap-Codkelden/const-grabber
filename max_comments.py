#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Calculation max number of the comments
"""

import json
import sys
from db_handle import db_handle

def max_comments():
	db = db_handle()

	db.create_user_list()
	db.cursor.execute("SELECT u.uname, COUNT(c.mid)  FROM users u \
		LEFT OUTER JOIN comments c \
		ON u.uid = c.uid \
		GROUP BY u.uid, u.uname \
		ORDER BY 2 DESC")
	mc = db.cursor.fetchall()
	db.delete_user_list()

	with open("max_comments.json", 'w') as mc_file:
		json.dump(mc, mc_file,  ensure_ascii=False)
	sys.stdout.write('Data saved in max_comments.json\n')


if __name__ == "__main__":
	max_comments()