import google
import plugincon
import praw
import requests
import BeautifulSoup
import json

try:
	ci, cs = open("praw_auth.txt").readlines()[:2]
	r = praw.Reddit(user_agent='GusPIRC-byGustavo6046', client_id=ci, client_secret=cs)

except IOError:
	r = praw.Reddit(user_agent='GusPIRC-Anonymous', client_id='DO_NOT_TRACK_THIS_DEVICE')

@plugincon.easy_bot_command("webabout")
def get_hot_from_subreddit(message, raw):
	if raw:
		return

	print "Getting from subreddit..."

	try:
		return ["Hot from /r/{}! (Found in Reddit) || ".format("".join(message["arguments"][2:])) + " | ".join([str(x) for x in r.get_subreddit("".join(message["arguments"][2:]).lower()).get_hot(limit=min([int(message["arguments"][1]), 10]))])]

	except IndexError:
		return "Syntax: webabout <num_hots> <topic>"

	try:
		gs = google.search(" ".join(message["arguments"][2:]), num=min([int(message["arguments"][1]), 5]), start=0, stop=min([int(message["arguments"][1]), 5]), pause=2)

	except IndexError:
		return "Syntax: webabout <num_hots> <topic>"

	print "Got Google search!"

	results = []

	for website in gs:
		request = requests.get(str(website))

		print "Parsing website: {}".format(str(website))

		try:
			results.append("{} -> {}".format(str(website.encode("utf-8")), BeautifulSoup.BeautifulSoup(request.text.encode("utf-8")).title.string.encode("utf-8")))

		except AttributeError:
			results.append(website.encode("utf-8") + " (No URL!)")

	return "Hot about {}! (Found in Google) || ".format(" ".join(message["arguments"][2:])) + " | ".join(results)
