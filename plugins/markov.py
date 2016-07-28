import json
import BeautifulSoup
import requests
import re

def visible(element):
    if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
        return False
    elif re.match('<!--.*-->', str(element)):
        return False
    return True

from plugincon import bot_command, easy_bot_command, get_message_target, get_bot_nickname
from random import choice, sample

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


markov_dict = {}

@bot_command("parsemarkov")
def parse_markov_from_text(message, connector, index, raw):
	global markov_dict

	if not raw:
		if len(message["arguments"]) < 2:
			connector.send_message(index, get_message_target(connector, message, index), "{}: Error: No argument provided!".format(message["nickname"]))
	
		for line in open(" ".join(message["arguments"][1:])).readlines():
			words = line.split(" ")
		
			for x in xrange(len(words) - 1):
				words[x] = string_filter(words[x].split(" "),
										   lambda y: not (not y.isalnum() and string_filter(y, "\'\"-/\\,.!?") == ""))

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

@bot_command("mkfeeder_on", False, True, True)
def feed_markov_data(message, connector, index, raw):
	global markov_dict

	if not raw:
		for x in xrange(len(message["arguments"]) - 1):
			message["arguments"][x] = string_filter(message["arguments"][x].split(" "),
									   lambda y: not (not y.isalnum() and string_filter(y, "\'\"-/") == ""))

		for x in xrange(len(message["arguments"])):
			try:
				if message["arguments"][x - 1] == message["arguments"][x] or message["arguments"][x] == message["arguments"][x + 1]:
					continue
			except IndexError:
				pass

			try:
				markov_dict[message["arguments"][x - 1].lower()].add(message["arguments"][x].lower())
			except KeyError:
				try:
					markov_dict[message["arguments"][x - 1].lower()] = {message["arguments"][x].lower()}
				except IndexError:
					pass
			except IndexError:
				pass

			try:
				markov_dict[message["arguments"][x].lower()].add(message["arguments"][x + 1].lower())
			except KeyError:
				try:
					markov_dict[message["arguments"][x].lower()] = {message["arguments"][x + 1].lower()}
				except IndexError:
					pass
			except IndexError:
				continue
				
@bot_command("markov")
def get_markov(message, connector, index, raw):
	global markov_dict

	if not raw:
		try:
			markov_dict.__delitem__("")
		except KeyError:
			pass

		if len(message["arguments"]) < 2:
			connector.send_message(index, message["channel"], "{0}: What topic?".format(message["nickname"]))

		else:
			try:
				x = string_filter(message["arguments"][1].lower(),
								  lambda x: not (not x.isalnum() and string_filter(x, "\'\"-/\\,.!?") == ""))
				markov_dict[string_filter(message["arguments"][1].lower(),
								  lambda x: not (not x.isalnum() and string_filter(x, "\'\"-/\\,.!?") == ""))]


			except KeyError:
				connector.send_message(index, message["channel"],
									   "{0}: The topic {1} isn't registered in my database.".format(message["nickname"],
																									message["arguments"][1]))

			else:
				phrase = string_filter(message["arguments"][1].lower(),
									   lambda x: not (not x.isalnum() and string_filter(x, "\'\"-/\\,.!?") == ""))
				i = 0

				while True:
					debuginfo = u"{0}: {1}".format(x, phrase)
					i += 1

					try:
						x = string_filter(sample(markov_dict[x], 1)[0],
										  lambda x: not (not x.isalnum() and string_filter(x, "\'\"-/\\,.!?") == ""))
						if x == phrase.split(" ")[-1]:
							raise RuntimeError
						if i > 99:
							raise RuntimeError

					except (KeyError, RuntimeError):
						connector.send_message(index, message["channel"], u"{0}: {1}".format(message["nickname"], phrase).encode("utf-8"))
						break

					phrase = u"{0} {1}".format(phrase, x)

					del debuginfo
					
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
		
@bot_command("parsewebmarkov")
def parse_web_markov(message, connector, index, raw):
	global markov_dict
	
	if not raw:
		if len(message["arguments"]) < 2:
			connector.send_message(index, get_message_target(connector, message, index), "{}: Error: No argument provided!".format(message["nickname"]))
			return
	
		try:
			request = requests.get(" ".join(message["arguments"][1:]))
			
		except requests.ConnectionError:
			connector.send_message(index, get_message_target(connector, message, index), "{}: URL missing or connection errored out!".format(message["nickname"]))
	
		if request.status_code != 200:
			connector.send_message(index, get_message_target(connector, message, index), "{}: Error: Status {} reached!".format(message["nickname"], request.status_code))
			return
	
		visible_texts = [text.encode("utf-8") for text in filter(visible, BeautifulSoup.BeautifulSoup(request.text).findAll(text=True))]
	
		lines = []
		
		for text in visible_texts:
			lines += text.split("\n")
	
		for line in lines:
			words = line.split(" ")
		
			for x in xrange(len(words) - 1):
				words[x] = string_filter(words[x].split(" "),
										   lambda y: not (not y.isalnum() and string_filter(y, "\'\"-/\\,.!?") == ""))

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
		
		connector.send_message(index, get_message_target(connector, message, index), "{}: Success reading Markov from website!".format(message["nickname"]))
		
@easy_bot_command("markovsize")
def get_markov_size(message, raw):
	global markov_dict

	if not raw:
		return ["Size of Markov chain: {}".format(len(markov_dict.keys()))]