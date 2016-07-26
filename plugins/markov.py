import json

from plugincon import bot_command, easy_bot_command
from random import choice


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

@bot_command(None, False, True, True)
def feed_markov_data(message, connector, index, raw):
	global markov_dict

	if not raw:
		for x in xrange(len(message["arguments"]) - 1):
			message["arguments"][x] = string_filter(message["arguments"][x].split(" "),
									   lambda y: not (not y.isalnum() and string_filter(y, "\'\"-/") == ""))

		for x in xrange(len(message["arguments"])):
			try:
				if message["arguments"][x - 1] == message["arguments"][x] or message["arguments"][x] == message["arguments"][x + 1] or message["arguments"][x - 1] == message["arguments"][x + 1]:
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
			connector.sendmessage(index, message["channel"], "{0}: What topic?".format(message["nick"]))

		else:
			try:
				x = string_filter(message["arguments"][1].lower(),
								  lambda x: not (not x.isalnum() and string_filter(x, "\'\"-/") == ""))
				markov_dict[string_filter(message["arguments"][1].lower(),
								  lambda x: not (not x.isalnum() and string_filter(x, "\'\"-/") == ""))]


			except KeyError:
				connector.sendmessage(index, message["channel"],
									   "{0}: The topic {1} isn't registered in my database.".format(message["nick"],
																									message["arguments"][1]))

			else:
				phrase = string_filter(message["arguments"][1].lower(),
									   lambda x: not (not x.isalnum() and string_filter(x, "\'\"-/") == ""))
				i = 0

				while True:
					debuginfo = u"{0}: {1}".format(x, phrase)
					i += 1

					try:
						x = string_filter(sample(markov_dict[x], 1)[0],
										  lambda x: not (not x.isalnum() and string_filter(x, "\'\"-/") == ""))
						if x == phrase.split(" ")[-1]:
							raise RuntimeError
						if i > 99:
							raise RuntimeError

					except (KeyError, RuntimeError):
						connector.sendmessage(index, message["channel"], u"{0}: {1}".format(message["nick"], phrase).encode("utf-8"))
						break

					phrase = u"{0} {1}".format(phrase, x)

					del debuginfo
					
@easy_bot_command("savemarkov")
def save_markov_json(message, raw):
	global markov_dict
	
	if not raw:
		if len(message["arguments"]) < 2:
			return ["Error: not enough arguments!", "(Insert Markov file name as an argument)"]
	
		json.dump(markov_dict, "{}.mkov2".format(message[arguments][1]))
		
		return ["Saved succesfully to {}.mkov2!".format(message[arguments][1])]
		
	else:
		return []
		
@easy_bot_command("loadmarkov")
def load_markov_json(message, raw):
	global markov_dict
	
	if not raw:
		if len(message["arguments"]) < 2:
			return ["Error: not enough arguments!", "(Insert Markov file name as an argument)"]
	
		markov_dict += json.load("{}.mkov2".format(message["arguments"][1]))
		
		return ["Loaded succesfully from {}.mkov2!".format(message["arguments"][1])]
		
	else:
		return []