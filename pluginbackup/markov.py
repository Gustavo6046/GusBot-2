import json
import BeautifulSoup
import requests
import re
import time
import threading

from plugincon import bot_command, easy_bot_command, get_message_target, get_bot_nickname
from random import choice, sample

markov_dict = {}
markov_filter = []

can_crawl = True

def regex(value, reg):
    if reg == "":
        return True

    return bool(re.search(reg, value))


def ends_with_any(string, list_of_endings):
    for ending in list_of_endings:
        if string.endswith(ending):
            return True

    return False

def visible(element):
    if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
        return False
    elif re.match('<!--.*-->', str(element)):
        return False
    return True

def isalnumspace(string):
	for char in string:
		if not (char.isalnum() or " " == char):
			return False
			
	return True

def simple_string_filter(old_string, bad_chars=None, extra_filter=None):
	result = ""
	
	if bad_chars:
		for char in old_string:
			if not char in bad_chars:
				result += char
			
	if extra_filter and hasattr(extra_filter, "__call__"):
		old_result = result
		result = ""
	
		for char in old_result:
			if extra_filter(char):
				result += char
			
	return result
	
def parse_markov_string(string):
	global markov_dict
	
	words = simple_string_filter(string, "\'\"-/\\,.!?", isalnumspace).split(" ")

	for x in xrange(len(words)):
		try:
			if words[x - 1] == words[x] or words[x] == words[x + 1]:
				continue
		except IndexError:
			pass

		try:
			markov_dict[words[x - 1].lower()].add(words[x].lower())
		except KeyError:
			try:
				markov_dict[words[x - 1].lower()] = {words[x].lower()}
			except IndexError:
				pass
		except IndexError:
			pass

		try:
			markov_dict[words[x].lower()].add(words[x + 1].lower())
		except KeyError:
			try:
				markov_dict[words[x].lower()] = {words[x + 1].lower()}
			except IndexError:
				pass
		except IndexError:
			continue
	
def string_filter(old_string, filter_, separator=None):
    result_string = []

    if hasattr(filter_, "__call__"):
        for x in old_string:
            if filter_(x):
                result_string.append(x)

    else:
        if separator is None:
            for x in old_string:
                if x in str(filter_):
                    result_string.append(x)
        else:
            for x in old_string:
                if x in str(filter_).split(separator):
                    result_string.append(x)

    return "".join(result_string)
	
def crawl_markov(website, url_mask, max_level=3, level=0, crawled_urls=[]):
	global markov_dict
	
	if level > max_level:
		return
	
	if not can_crawl:
		return
	
	warnings = []
	time.sleep(0.4)
	
	try:
		request = requests.get(website.encode("utf-8"), timeout=10)
		
	except requests.ConnectionError:
		return
		
	except requests.exceptions.Timeout:
		return
		
	except (requests.exceptions.MissingSchema, requests.exceptions.InvalidURL):
		try:
			request = requests.get("http://" + website.encode("utf-8"), timeout=10)
			
		except requests.ConnectionError:
			return
			
		except requests.exceptions.Timeout:
			return
			
		except requests.exceptions.InvalidURL:
			return
	
	html = BeautifulSoup.BeautifulSoup(request.text.encode("utf-8"))
	
	for link in html.findAll("a", {"href": True}):
		url = link["href"].encode("utf-8'")
		
		if re.match("\.[a-zA-Z1-9]+$", url) and not url.endswith(".html"):
			continue
		
		if not url.startswith("http"):
			continue
			
		if url in crawled_urls:
			continue
			
		crawled_urls.append(url)
		
		if regex(url, url_mask):
			threading.Thread(target=crawl_markov, args=(url, url_mask, max_level, level+1, crawled_urls)).start()
			
	for visible_text in [text.encode("utf-8") for text in filter(visible, html.findAll(text=True))]:
		for line in visible_text.splitlines():
			parse_markov_string(line)
			
	print "Done crawling {}!".format(website)
	
@easy_bot_command("togglemarkovcrawling")
def toggle_crawling(message, raw):
	global can_crawl
	
	if raw:
		return
	
	can_crawl = not can_crawl
	
	return "Success: now crawling is{} stopped!".format(("n't" if can_crawl else ""))
	
@bot_command("parsemarkov")
def parse_markov_from_text(message, connector, index, raw):
	global markov_dict
	
	for key, item in markov_dict.items():
			markov_dict[key] = set(item)

	if not raw:
		if len(message["arguments"]) < 2:
			connector.send_message(index, get_message_target(connector, message, index), "{}: Error: No argument provided!".format(message["nickname"]))
	
		for line in open(" ".join(message["arguments"][1:])).readlines():
			words = simple_string_filter(line, "\'\"-/\\,.!?", isalnumspace).split(" ")

			for x in xrange(len(words)):
				try:
					if words[x - 1] == words[x] or words[x] == words[x + 1]:
						continue
				except IndexError:
					pass

				try:
					markov_dict[words[x - 1].lower()].add(words[x].lower())
				except KeyError:
					try:
						markov_dict[words[x - 1].lower()] = {words[x].lower()}
					except IndexError:
						pass
				except IndexError:
					pass

				try:
					markov_dict[words[x].lower()].add(words[x + 1].lower())
				except KeyError:
					try:
						markov_dict[words[x].lower()] = {words[x + 1].lower()}
					except IndexError:
						pass
				except IndexError:
					continue
		
		connector.send_message(index, get_message_target(connector, message, index), "{}: Text file succesfully parsed on Markov!".format(message["nickname"]))

@easy_bot_command("flushmarkov", True)
def flush_markov_data(message, raw):
	global markov_dict
	
	if raw:
		return

	markov_dict = {}
	
	return ["Markov flushed succesfully!"]
	
@bot_command("mk_feeder", False, True, True)
def feed_markov_data(message, connector, index, raw):
	global markov_dict
	
	if raw:
		return
	
	for key, item in markov_dict.items():
			markov_dict[key] = set(item)

	if not raw:
		words = simple_string_filter(" ".join(message["arguments"]), "\'\"-/\\,.!?", isalnumspace).split(" ")

		for x in xrange(len(words)):
			if x - 1 > -1:			
				try:
					if words[x - 1] == words[x] or words[x] == words[x + 1]:
						continue
				except IndexError:
					pass

				try:
					markov_dict[words[x - 1].lower()].add(words[x].lower())
				except KeyError:
					try:
						markov_dict[words[x - 1].lower()] = {words[x].lower()}
					except IndexError:
						pass
				except IndexError:
					pass

				try:
					markov_dict[words[x].lower()].add(words[x + 1].lower())
				except KeyError:
					try:
						markov_dict[words[x].lower()] = {words[x + 1].lower()}
					except IndexError:
						pass
				except IndexError:
					continue
			
			else:
				try:
					markov_dict[words[x].lower()].add(words[x + 1].lower())
				except KeyError:
					try:
						markov_dict[words[x].lower()] = {words[x + 1].lower()}
					except IndexError:
						pass
				except IndexError:
					continue
				
@easy_bot_command("markov")
def get_markov(message, raw):
	global markov_dict
	
	for key, item in markov_dict.items():
			markov_dict[key] = set(item)

	if raw:
		return
		
	# Checks.
	try:
		markov_dict.__delitem__("")
		
	except KeyError:
		pass

	if len(markov_dict) < 1:
		return "\x035\x02Error\x02\x03: no Markov data!"
		
	# Get the string!
	if len(message["arguments"]) < 2:
		x = choice(markov_dict.keys())
		words = [x]
		
	else:
		words = message["arguments"][1:]
		x = words[0]
			
	level = 0
	result = "{0}: ".format(message["nickname"]) + x
	
	print x
	
	while level < len(words) - 1:
		if not words[level + 1] in markov_dict[x]:
			return [result]
			
		print x
			
		x = words[level + 1]
		level += 1
		result += " " + x
		
	while x in markov_dict.keys():
		x = sample(markov_dict[x], 1)[0]
		
		print x
		
		result += " " + x
		
		level += 1
		
		if level > 70:
			break
			
	for cuss in markov_filter:
		print "Filtering {cuss} from {string}!".format(cuss=cuss, string=result)
		result = result.replace(cuss, "*")
			
	return [result]
	
					
@easy_bot_command("savemarkov")
def save_markov_json(message, raw):
	global markov_dict
	
	if not raw:
		if len(message["arguments"]) < 2:
			return ["Error: not enough arguments!", "(Insert Markov file name as an argument)"]
	
		save_dict = markov_dict
		
		for key, item in save_dict.items():
			save_dict[key] = tuple(item)
	
		open("{}.mkov2".format(message["arguments"][1]), "w").write(json.dumps(save_dict))
		
		for key, item in markov_dict.items():
			markov_dict[key] = set(item)
		
		return ["{}: Saved succesfully to {}.mkov2!".format(message["nickname"], message["arguments"][1])]
		
	else:
		return []
		
@easy_bot_command("loadmarkovfilter")
def load_markov_filter(message, raw):
	global markov_filter

	if raw:
		return
		
	if len(message["arguments"]) < 2:
		return ["Error: Not enough arguments!"]
		
	markov_filter += open(" ".join(message["arguments"][1:])).read().splitlines()
		
	return ["Blacklist updated succesfully!"]
	
@easy_bot_command("savemarkovfilter")
def save_markov_filter(message, raw):
	global markov_filter
	
	if raw:
		return
		
	if len(message["arguments"]) < 2:
		return ["Error: Not enough arguments!"]
		
	open(" ".join(message["arguments"][1:]), "w").write("\n".join(markov_filter))
		
	return ["Blacklist updated succesfully!"]
		
@easy_bot_command("loadmarkov")
def load_markov_json(message, raw):
	global markov_dict
	
	if not raw:
		if len(message["arguments"]) < 2:
			return ["Error: not enough arguments!", "(Insert Markov file name as an argument)"]
	
		new_dict = json.load(open("{}.mkov2".format(message["arguments"][1])))
		
		for key, item in new_dict.items():
			new_dict[key] = {word for word in item}
		
		markov_dict.update(new_dict)
		
		return ["Loaded succesfully from {}.mkov2!".format(message["arguments"][1])]
		
	else:
		return []
		
@easy_bot_command("listfiltermarkov")
def list_cusses(message, raw):
	if raw:
		return
		
	return "Cusses blacklisted: " + ", ".join(markov_filter)
		
@easy_bot_command("addfiltermarkov")
def filter_cusses(message, raw):
	if raw:
		return
		
	global markov_filter
	
	try:
		markov_filter += message["arguments"][1:]
		return ["Updated word blacklist succesfully!"]
		
	except IndexError:
		return ["Syntax: addfiltermarkov <list of cusses or blacklisted words>"]
		
@easy_bot_command("removefiltermarkov")
def unfilter_cusses(message, raw):
	if raw:
		return
		
	global markov_filter
	
	try:
		for cuss in message["arguments"][1:]:
			markov_filter.remove(cuss)
			
		return ["Updated word blacklist succesfully!"]
		
	except IndexError:
		return ["Syntax: removefiltermarkov <list of words to un-blacklist>"]
		
@easy_bot_command("parsewebmarkov")
def parse_web_markov(message, raw):
	global markov_dict
	
	for key, item in markov_dict.items():
			markov_dict[key] = set(item)
	
	if raw:
		return
			
	messages = []
	warnings = []
			
	debug = "--debug" in message["arguments"][1:]
			
	if len(message["arguments"]) < 2:
		return ["{}: Error: No argument provided! (Syntax: parsewebmarkov <list of URLs>)".format(message["nickname"])]
			
	for website in filter(lambda x: not x.startswith("--"), message["arguments"][1:]):
		print "Parsing Markov from {}!".format(website)
		messages.append("Parsing Markov from {}!".format(website))
	
		try:
			request = requests.get(website, timeout=10)
			
		except requests.ConnectionError:
			warnings.append("Error with connection!")
			
			if debug:
					raise
			
		except requests.exceptions.Timeout:
			warnings.append("Connection timed out!")
			
			if debug:
					raise
			
		except requests.exceptions.MissingSchema:
			try:
				request = requests.get("http://" + website, timeout=10)
				
			except requests.ConnectionError:
				warnings.append("Error with connection!")
				
				if debug:
					raise
				
			except requests.exceptions.Timeout:
				warnings.append("Connection timed out!")
				
				if debug:
					raise

		if not "request" in locals().keys():
			continue
				
		if request.status_code != 200:
			warnings.append("{}: Error: Status {} reached!".format(message["nickname"], request.status_code))
			continue
		
		visible_texts = [text.encode("utf-8") for text in filter(visible, BeautifulSoup.BeautifulSoup(request.text).findAll(text=True))]
	
		lines = []
		
		for text in visible_texts:
			lines += text.split("\n")
	
		for line in lines:
			words = simple_string_filter(line, "\'\"-/\\,.!?", isalnumspace).split(" ")

			for x in xrange(len(words)):
				try:
					if words[x - 1] == words[x] or words[x] == words[x + 1]:
						continue
				except IndexError:
					pass

				try:
					markov_dict[words[x - 1].lower()].add(words[x].lower())
				except KeyError:
					try:
						markov_dict[words[x - 1].lower()] = {words[x].lower()}
					except IndexError:
						pass
				except IndexError:
					pass

				try:
					markov_dict[words[x].lower()].add(words[x + 1].lower())
				except KeyError:
					try:
						markov_dict[words[x].lower()] = {words[x + 1].lower()}
					except IndexError:
						pass
				except IndexError:
					continue
			
	if len(warnings) < len(message["arguments"][1:]):
		messages.append("{}: Success reading Markov from (some) website(s)!".format(message["nickname"]))
			
	return messages + warnings
		
@easy_bot_command("parsewebmarkovcrawl", True)
def get_web_markov_crawling(message, raw):
	if raw:
		return
	
	time.sleep(0.3)
	
	if len(message["arguments"]) < 4:
		return "Syntax: <URL mask> <max level> <list of URLs to crawl for Markov>"
		
	try:
		if int(message["arguments"][2]) > 4:
			return "Way too large value for max_level! Use only up to 4. Do you want to wait for an eternity?!?"
			
		if int(message["arguments"][2]) < 0:
			return "Lol negative level XD"
			
	except ValueError:
		return "Insert some int for max level (second argument)! Insert something between 0 and 4."
		
	for website in message["arguments"][3:]:
		crawl_markov(website, message["arguments"][1], int(message["arguments"][2]))
		
	return "Website crawling threads started! Check for new additions using ||markovsize ."
		
@easy_bot_command("markovsize")
def get_markov_size(message, raw):
	global markov_dict

	if not raw:
		return ["Size of Markov chain: {}".format(len(markov_dict.keys()))]