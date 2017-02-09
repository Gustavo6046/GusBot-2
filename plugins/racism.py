import plugincon
import json
import BeautifulSoup
import requests
import re
import random

# Racism | Requested by Chrisella, not recommended for normal users

enabled = False

racist_words = []
racist_links = {}

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

def visible(element):
    if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
        return False
		
    elif re.match('<!--.*-->', str(element)):
        return False
		
    return True

def sections(i, l, join=False):
	result = []
	sub = []
	n = 1
	
	for item in i:
		sub.append(item)
	
		if n == l:
			result.append(sub)
			sub = []
			
			if join:
				sub.append(item)
	
		n += 1
		
	return result
	
def random_racism():
	global racist_words, racist_links

	sentence = []

	for word in random.sample(racist_words, len(racist_words)):
		print word
	
		sentence.append(word)
		
		if len(" ".join(sentence)) > 250:
			return " ".join(sentence)
		
		if word not in racist_links.keys():
			continue
		
		while word in racist_links.keys():
			word = random.choice(racist_links[word])
		
			sentence.append(word)
	
			if len(" ".join(sentence)) > 250:
				return " ".join(sentence)

	print " ".join(sentence)
	
	if sentence == []:
		raise RuntimeError("No sentence formed!")
	
	return sentence

@plugincon.easy_bot_command("save_racism")
def save_racism(message, raw):
	global racist_links, racist_words

	if raw:
		return
		
	if len(message["arguments"]) < 2:
		return "Name of file to save Racism to!"
		
	result = {"links": racist_links, "words": racist_words}
	open(" ".join(message["arguments"][1:]) + ".mkov3", "w").write(json.dumps(result))
		
	return "Saved succesfully to: " + " ".join(message["arguments"][1:]) + ".mkov3"

@plugincon.easy_bot_command("load_racism")
def load_racism(message, raw):
	global racist_links, racist_words

	if raw:
		return
		
	if len(message["arguments"]) < 2:
		return "Name of file to load Racism from!"
		
	try:
		new = json.load(open(" ".join(message["arguments"][1:]) + ".mkov3"))
		
	except IOError:
		return "File not existant!"
		
	racist_links.update(new["links"])
	racist_words += new["words"]
	return "Loaded succesfully from: " + " ".join(message["arguments"][1:]) + ".mkov3"
	
@plugincon.easy_bot_command("parse_web_racism")
def parse_web_racism(message, raw):
	global racist_words, racist_links

	if raw:
		return
	
	if len(message["arguments"]) < 2:
		return "Syntax: ||parse_web_racism <website>, [<website>, [...]]>"
		
	warnings = []
		
	for website in " ".join(message["arguments"][1:]).split(", "):
		try:
			request = requests.get(website, timeout=10)
			
		except requests.ConnectionError:
			warnings.append("Error with connection ({website})!".format(website=website))
			
		except requests.exceptions.Timeout:
			warnings.append("Connection timed out ({website})!".format(website=website))
			
		except requests.exceptions.MissingSchema:
			try:
				request = requests.get("http://" + website, timeout=10)
				
			except requests.ConnectionError:
				warnings.append("Error with connection ({website})!".format(website=website))
				
			except requests.exceptions.Timeout:
				warnings.append("Connection timed out ({website})!".format(website=website))
					
		if not "request" in locals().keys():
			continue
			
		if request.status_code != 200:
			warnings.append("Status {} reached ({})!".format(request.status_code, website))
			continue
			
		visible_texts = [text.encode("utf-8") for text in filter(visible, BeautifulSoup.BeautifulSoup(request.text).findAll(text=True))]
	
		lines = []
		
		for text in visible_texts:
			lines += text.split("\n")
	
		for line in lines:
			words = simple_string_filter(line, "\'\"-/\\,.!?", isalnumspace).split(" ")
			
			racist_words += words
			
			for key, item in dict(sections(words, 2, True)).items():
				if key not in racist_links.keys():
					racist_links[key] = [item]
				
				else:
					racist_links[key].append(item)
		
	messages = warnings
		
	if len(warnings) < len(" ".join(message["arguments"][1:]).split(", ")):
		messages.append("Parsed websites succesfully!")
	
	return messages
	
@plugincon.easy_bot_command("link_racism")
def link_racism(message, raw):
	global racist_links

	if raw:
		return
	
	if len(message["arguments"][1:]) < 1:
		return "What words to link?"
		
	for key, item in dict(sections(message["arguments"][1:], 2, True)).items():
		if key not in racist_links.keys():
			racist_links[key] = [item]
		
		else:
			racist_links[key].append(item)
	
	return "Words linked succesfully: " + "; ".join([": ".join([x, ", ".join(y)]) for x, y in racist_links.items()])

@plugincon.easy_bot_command("add_racism")
def add_racism(message, raw):
	if raw:
		return
	
	if len(message["arguments"][1:]) < 1:
		return "What words to add?"
		
	for word in message["arguments"][1:]:
		racist_words.append(word)
	
	return "Racist words added succesfully! Feel free to link them with ||link_racism ."

@plugincon.easy_bot_command("toggle_racism")
def toggle_racism(message, raw):
	global enabled

	if raw:
		return
	
	if enabled:
		enabled = False
	
		return "Racism disabled!"
		
	enabled = True
	
	return "Racism enabled! Kick ass with ||racism now!"
	
@plugincon.easy_bot_command("racism")
def racism(message, raw):
	global enabled

	if raw:
		return
	
	if not enabled:
		return "Enable with ||toggle_racism first!"
		
	try:
		result = random_racism()
		print result
		
		return result
	
	except RuntimeError:
		return "Error: No racism data found!"