from plugincon import easy_bot_command, bot_command, get_message_target
from Queue import Queue

listener_targets = {}

@easy_bot_command("addlistener", True)
def add_listeners(message, raw):
	if raw:
		return
	
	if len(message["arguments"]) < 3:
		return "Syntax: addlistener <in channel> <out channel>"
		
	in_chan = message["arguments"][1]
	out_chan = message["arguments"][2]
		
	try:
		listener_targets[in_chan].append(out_chan)
		
	except KeyError:
		listener_targets[in_chan] = [out_chan]
		
	return ["Listener added succesfully!"]
	
@easy_bot_command("removelistener", True)
def add_listeners(message, raw):
	if raw:
		return
	
	if len(message["arguments"]) < 3:
		return "Syntax: removelistener <in channel> <out channel>"
		
	in_chan = message["arguments"][1]
	out_chan = message["arguments"][2]
		
	try:
		listener_targets[in_chan].remove(out_chan)
		
	except ValueError:
		return "No such listener out channel!"
		
	except KeyError:
		return "No such listener in channel!"
	
	if listener_targets[in_chan] == []:
		listener_targets.__delitem__(in_chan)
		
	return ["Listener removed succesfully!"]
	
@bot_command("ListenerParse", False, True, True)
def listener_parsing(message, connector, index, raw):
	def message_target(msg, target=None):
		if not target:
			target = get_message_target(connector, message, index)
			
		connector.send_message(index, target, msg)
		
	if raw:
		return
	
	try:
		for target in listener_targets[message["channel"]]:
			message_target("<{}> {}".format(message["nickname"], message["message"]), target)

	except KeyError:
		pass