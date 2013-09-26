import json
from db_handle import db_handle
import sys

# график по месяцам по количеству постов/комментариев. без указаания кто

def posts_per_user():
	db = db_handle()
	db.create_user_list()
	db.cursor.execute("SELECT u.uname, COUNT(p.mid)  FROM users u \
		LEFT OUTER JOIN posts p \
		ON u.uid = p.uid \
		GROUP BY u.uid, u.uname \
		ORDER BY 2 DESC")
	ppu = db.cursor.fetchall()
	db.delete_user_list()

	with open("posts_per_user.json", 'w') as ppu_file:
		json.dump(ppu, ppu_file,  ensure_ascii=False)
	sys.stdout.write('Data saved in posts_per_user.json\n')

if __name__ == "__main__":
	posts_per_user()