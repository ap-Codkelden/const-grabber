 #!/usr/bin/env python
 # -*- coding: utf-8 -*-

import urllib.request
import json

TAG_URL = """http://api.juick.com/messages?tag=%D1%81%D0%BE%D0%B7%D0%B2%D0%B5%D0%B7%D0%B4%D0%B8%D0%B5&page="""


i = 1
post_numbers = []
posts_with_comments = []


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

if __name__ == "__main__":
	while True:
		try:
			content = GetContent(TAG_URL, i)
			GetNumbers(content)
			i+=1
		except urllib.error.HTTPError:
			break

	for post_number in post_numbers:
		posts_with_comments.append(GetMessageWithComments(post_number)[0:])

	print("%s posts processed." % len(post_numbers))

	with open('data.txt', 'w') as outfile:
		json.dump(posts_with_comments, outfile, ensure_ascii=False, indent=1)