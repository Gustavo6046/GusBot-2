import time
import json
import random

from plugincon import easy_bot_command, bot_command

num_nodes = 0

try:
	word_data = json.load(open("chains.json"))
	
except (IOError, ValueError):
	word_data = {}
	
for word, item in word_data.items():
	word_data[word]["markov"] = set(item["markov"])
	word_data[word]["nodes"] = set(item["markov"])

def isalnumspace(string):
	for char in string:
		if not (char.isalnum() or " " == char):
			return False
			
	return True
	
def add_markov_chaining(word1, word2):
	try:
		word_data[word1]["markov"].add(word2)
		
	except KeyError:
		word_data[word1]["markov"] = {word2}
	
def parse_sentence(sentence):
	global word_data
	global num_nodes
	
	words = "".join(filter(isalnumspace, sentence)).lower().split(" ")
	words = filter(lambda x: x not in ("", " "), words)
	
	if len(words) < 2:
		return
	
	for i, word in enumerate(words):
		if word not in word_data.keys():
			word_data[word] = {
				"nodes": set(),
				"markov": set()
			}
	
		for second_word in words:
			new_node = False
		
			if len(word_data[word]["nodes"]) == 0:
				word_data[word]["nodes"] = {num_nodes}
				new_node = True
		
			try:
				if len(word_data[second_word]["nodes"]) == 0:
					word_data[second_word]["nodes"] = {num_nodes}
					
				new_node = True
				
			except KeyError:
				word_data[second_word] = {
					"nodes": set([num_nodes]),
					"markov": set()
				}
				new_node = True
				
			word_data[word]["nodes"] = word_data[word]["nodes"] | word_data[second_word]["nodes"]
				
			if new_node:
				num_nodes += 1
					
		try:		
			if words[i - 1] != -1:
				add_markov_chaining(words[i - 1], word)
		
		except (IndexError, KeyError):
			pass
			
		try:		
			add_markov_chaining(word, words[i + 1])
		
		except IndexError:
			pass
			
def set_matches(set_1, set_2):
	return len(set_1 & set_2)
			
def request_sentence(start_word):
	result = start_word
	word = start_word

	while len(result) < 451:
		past_word = word
		
		n = 0
		while True:
			try:
				print word_data[word]["markov"]
				
				word = random.sample(word_data[word]["markov"], 1)[0]
				
			except (ValueError, IndexError):
				n += 1
				
				if n > 50:
					return "Failure retrieving string!"
				
				continue
			
			break
			
		try:
			best_word = sorted({x: set_matches(word_data[x]["nodes"], word_data[word]["nodes"]) for x in word_data[word]["markov"]}.items(), lambda x, y: y[1])[-1]
			
		except KeyError:
			return "Error: No such word in my Rehermann chain!"
		
		print best_word[1]
		
		try:
			if best_word[1] == 0:
				break
				
		except IndexError:
			break
		
		word = best_word[0]
		result += " " + word
			
	return result

@bot_command("mann_feeder", False, True, True)
def feed_markov_data(message, connector, index, raw):
	global markov_dict
	
	if raw:
		return
	
	parse_sentence(" ".join(message["arguments"]))
	
	open("chains.json", "w").write(json.dumps({x: {"markov": list(y["markov"]), "nodes": list(y["nodes"])} for x, y in word_data.items()}))
	
@easy_bot_command("rehermannparse", True)
def parse_rehermann(message, raw):
	if raw:
		return
		
	try:
		for line in open(" ".join(message["arguments"][1:])).readlines():
			parse_sentence(line)
			
	except IOError:
		return "File not found!"
		
	open("chains.json", "w").write(json.dumps({x: {"markov": list(y["markov"]), "nodes": list(y["nodes"])} for x, y in word_data.items()}))
		
	return "Success parsing Rehermann from file!"
	
@easy_bot_command("rehermannreq")
def request_rehermann(message, raw):
	if raw:
		return
		
	if len(message["arguments"]) > 1:
		return "{}: {}".format(message["nickname"], request_sentence(message["arguments"][1]))
		
	else:
		return "{}: {}".format(message["nickname"], request_sentence(random.choice(word_data.keys())))