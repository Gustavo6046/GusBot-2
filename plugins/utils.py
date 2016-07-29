import requests

from plugincon import bot_command, easy_bot_command, get_message_target, get_bot_nickname
from BeautifulSoup import BeautifulSoup
from requests import get


@easy_bot_command("webtitle")
def website_title(message, raw):
	if raw:
		return
		
	if message["arguments"] < 2:
		return ["Too little arguments! Syntax: website_title <URL>"]

	try:
		request = get(" ".join(message["arguments"][1:]), timeout=10)
		
	except requests.ConnectionError:
		return ["Error with connection!"]
		
	except requests.exceptions.Timeout:
		return ["Connection timed out!"]
		
	except requests.exceptions.MissingSchema:
		try:
			request = get("http://" + " ".join(message["arguments"][1:]), timeout=10)
			
		except requests.ConnectionError:
			return ["Error with connection!"]
			
		except requests.exceptions.Timeout:
			return ["Connection timed out!"]

	if request.status_code != 200:
		return ["{}: Error: Status {} reached!".format(message["nickname"], request.status_code)]
		
	soup = BeautifulSoup(request.text)
		
	if not soup.title.string:
		return ["No webpage title!"]
		
	return ["Webpage's Title | {}".format(soup.title.string.encode("utf-8").replace("\n", ""))]