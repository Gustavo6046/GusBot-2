import json
import json

from collections import Counter

# Credits to Alex from SO ( http://stackoverflow.com/users/276118/alex ) for most_common solution ( http://stackoverflow.com/a/20872750/5129091 )

def isalnumspace(string):
	for char in string:
		if not (char.isalnum() or " " == char):
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