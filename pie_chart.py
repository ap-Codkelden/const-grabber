import json
import sqlite3
import sys


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

post_db = sqlite3.connect('post.db')
cursor = post_db.cursor()

if __name__ == "__main__":
	posts_per_user()