 #!/usr/bin/env python
 # -*- coding: utf-8 -*-

import urllib.request
import json

TAG_URL = """http://api.juick.com/messages?tag=%D1%81%D0%BE%D0%B7%D0%B2%D0%B5%D0%B7%D0%B4%D0%B8%D0%B5&page="""


i = 1

post_numbers = []
posts_with_comments = []
posts_processed_count = point_count = 0


def GetNumberOfStoredPosts():
	try:
		with open('posts', 'r') as post_numbers_storage:
			l = post_numbers_storage.readlines()
	except IOError:
		post_numbers_storage = open('posts', 'w')
		l = []
	post_numbers_storage.close()
	return l

def GetMessageWithComments(message_number):
	return GetContent("http://api.juick.com/thread?mid=%s" % (message_number))


def GetContent(url, number=''):
	text = urllib.request.urlopen(url + str(number))
	# костыль для \t от @mahury ;)
	raw_content = text.read().replace(b"\t", b"")
	readable = raw_content.decode('utf-8')
	json_data = json.loads(readable)
	return json_data


def GetNumbers(content):
	for i in content:
		post_numbers.append(i['mid'])
		post_numbers_storage.write(str(i['mid'])+'\n')


if __name__ == "__main__":
	
	stored_numbers = GetNumberOfStoredPosts()
	if len(stored_numbers) == 0:
		last_post = 0
	else:
		last_post = int(stored_numbers[0])

	post_numbers_storage = open('posts', 'w+')

	while True:
		try:
			content = GetContent(TAG_URL, i)
			GetNumbers(content)
			i+=1
		except urllib.error.HTTPError:
			print("%s page(s) total." % (i-1))
			break

	for post_number in post_numbers:
		if post_number > last_post:
			posts_with_comments.append(GetMessageWithComments(post_number)[0:])
			posts_processed_count += 1
			print(".", end="")
			point_count += 1
			if point_count % 20 == 0:
				print('.')



	print("\n\n%s posts processed, %s posts total." % (posts_processed_count, posts_processed_count+len(stored_numbers)))

	if posts_processed_count != 0:
		with open('constellation.json', 'r') as f:
			old_json_data = json.load(f)
		f.close()
		for post in posts_with_comments:
			old_json_data.append(post)

		with open('constellation.json', 'w') as outfile:
			json.dump(old_json_data, outfile, ensure_ascii=False, indent=1)


	post_numbers_storage.close()