import sqlite3

"""
(17445, 'ap-Codkelden', 17)
"""

def CheckDB():
	try:
		with open('post.db'):
			pass 
	except IOError:
		return False
	return True

class JuickPosts:
	def __init___(self):
		pass

	def Connect(self):
		try:
			self.post_db = sqlite3.connect("post.db")
			self.cursor = self.post_db.cursor()
		except:
			print("Something went wrong.")


	def CheckTable(self):
		self.cursor.execute("PRAGMA table_info(posts);")
		posts_table_data = self.cursor.fetchall()
		if len(posts_table_data)!=0:
			self.cursor.execute("SELECT * FROM posts;")
			posts = self.cursor.fetchall()
		if len(posts) != 0:
			return 1
		else:
			return 0

if __name__ == "__main__":
	if CheckDB():
		db_handle = JuickPosts()
		db_handle.Connect()
		#attrs = vars(db_handle)
		#print(', '.join("%s: %s" % item for item in attrs.items()))
		if db_handle.CheckTable():
			db_handle.create_tables()
