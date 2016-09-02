import requests
import BeautifulSoup
import re
import json
import plugincon
from collections import Counter

try:
	topic_words, answers, past_strings, num_topics = json.load(open("guschat.json"))
	
except (IOError, ValueError):
	topic_words = {}
	answers = []
	past_strings = []
	num_topics = 0

# Credits to Alex from SO ( http://stackoverflow.com/users/276118/alex ) for most_common solution ( http://stackoverflow.com/a/20872750/5129091 )

def isalnumspace(string):
	for char in string:
		if not (char.isalnum() or " " == char):
			return False
			
	return True

def visible(element):
    if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
        return False
    elif re.match('<!--.*-->', str(element)):
        return False
    return True
	
def most_common(lst):
	try:
		data = Counter(lst)
		return data.most_common(1)[0][0]
		
	except IndexError:
		return None
		
def parse_sentence_in_gc(sentence):
	global topic_words
	global answers
	global past_strings
	global num_topics
	
	open("guschat.json", "w").write(json.dumps((topic_words, answers, past_strings, num_topics)))

	words = filter(lambda x: x not in ("", " "), "".join(filter(isalnumspace, sentence)).lower().split(" "))
	
	new_topic = num_topics + 1
	current_topics = []
	untopiced_words = []
	
	for word in words:
		try:
			current_topics.append(topic_words[word])
	
		except KeyError:
			untopiced_words.append(word)
		
	for word in untopiced_words:
		topic_words[word] = new_topic
		current_topics.append(new_topic)
		
	if len(untopiced_words):
		num_topics += 1
		
	sentence_topic = most_common(current_topics)
		
	if not sentence_topic:
		sentence_topic = new_topic
	
	try:
		answers[sentence_topic][past_strings[-1]].append(words)
		
	except KeyError:
		try:
			try:
				answers[sentence_topic][past_strings[-1]] = [words]
			
			except KeyError:
				answers.append({past_strings[-1]: [words]})
				
		except IndexError:
			pass
			
	except IndexError:
		pass
		
	past_strings.append(words)
	
	open("guschat.json", "w").write(json.dumps((topic_words, answers, past_strings, num_topics)))

def answer_gc(sentence):
	global topic_words
	global answers
	global past_strings
	
	topic_words, answers, past_strings, num_topics = json.load(open("guschat.json"))

	words = filter(lambda x: x not in ("", " "), "".join(filter(isalnumspace, sentence)).lower().split(" "))
	
	current_topics = []
	
	for word in words:
		try:
			current_topics.append(topic_words[word])
	
		except KeyError:
			pass
		
	sentence_topic = most_common(current_topics)
	
	if not sentence_topic:
		return "\x02\x0305Error:\x03\x02 Sentence's topic not recognized!"
	
	try:
		answers[sentence_topic][past_strings[-1]].append(sentence)
	
	except IndexError:
		pass
		
	past_strings.append(words)
	
	result = max(past_strings, key=lambda x: len(list(set(x) & set(words))))
	
	print result
	
	result[0] = result[0][0].upper() + result[0][1:]
	result[-1] += "."
	
	open("guschat.json", "w").write(json.dumps((topic_words, answers, past_strings, num_topics)))
	return " ".join(result)
	
@plugincon.easy_bot_command("gc_feeder", False, True, True)
def parse_message_in_gc(message, raw):
	if raw:
		return

	parse_sentence_in_gc(message["body"])
	
@plugincon.easy_bot_command("guschat_talk")
def answer_message(message, raw):
	if raw:
		return
		
	if len(message["arguments"]) < 2:
		return "\x02\x0305Error:\x02\x03 What did you open your mouth for?"
	
	return str("{}: ".format(message["nickname"]) + answer_gc(" ".join(message["arguments"][1:])))
	
@plugincon.easy_bot_command("guschat_webparse", True)
def parse_from_web(message, raw):
	if raw:
		return
		
	warnings = []
	messages = []
		
	for website in filter(lambda x: not x.startswith("--"), message["arguments"][1:]):
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
		
		for text in [text.encode("utf-8") for text in filter(visible, BeautifulSoup.BeautifulSoup(request.text).findAll(text=True))]:
			for line in text.splitlines():
				parse_sentence_in_gc(line)
				
	if len(warnings) < len(message["arguments"][1:]):
		messages.append("{}: Success reading GusChat data from (some) website(s)!".format(message["nickname"]))
			
	return messages + warnings
	
@plugincon.easy_bot_command("guschat_clear", True)
def clear_gc_data(message, raw):
	if raw:
		return

	topic_words = {}
	answers = []
	past_strings = []
	num_topics = 0

	return "GusChat data cleared succesfully!"
	
@plugincon.easy_bot_command("guschat_parsefile", True)
def parse_gc_file(message, raw):
	if raw:
		return

	try:
		for line in open(" ".join(message["arguments"][1:])).readlines():
			parse_sentence_in_gc(line)
			
	except IOError:
		return "\x02\x0305Error:\x02\x03 No such file!"

	return "Parsed flie succesfully!"