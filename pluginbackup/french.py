from plugincon import bot_command, easy_bot_command, get_message_target, get_bot_nickname, reload_all_plugins
import json

french_db = {}

@easy_bot_command("teachfrench")
def teach_french(message, raw):
	if raw:
		return
		
	if message["arguments"] < 3:
		return ["It's teachfrench <english word> <french word>", "Don't worry. I know you can!"]
		
	french_db[message["arguments"][1]] = message["arguments"][2]
		
	return ["Added to database. Thanks! :)"]
	
@easy_bot_command("translatetofrench")
def translate_to_french(message, raw):
	if raw:
		return
		
	french_words = []
	untranslatable_words = []
		
	for word in message["arguments"][1:]:
		try:
			french_words.append(french_db[word])
			
		except KeyError:
			french_words.append(word)
			untranslatable_words.append(word)
		
	return ["Translated: " + " ".join(french_words)] + (["Words without findable translation: " + " ".join(untranslatable_words)] if untranslatable_words else [])
	
@easy_bot_command("savefrench")
def save_french_db(message, raw):
	if raw:
		return
		
	if message["arguments"] < 2:
		return ["It's savefrench <filename (without .json)>"]
		
	json.dump(french_db, open(" ".join(message["arguments"][1:]) + ".json", "w"))
	return ["Saved succesfully!"]
	
@easy_bot_command("loadfrench")
def load_frendh_db(message, raw):
	if raw:
		return
		
	if message["arguments"] < 2:
		return ["It's loadfrench <filename (without .json)>"]
		
	french_db.update(json.load(open(" ".join(message["arguments"][1:]) + ".json")))
	
	return "Loaded succesfully!"