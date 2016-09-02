from plugincon import easy_bot_command, bot_command, get_message_target
from Queue import Queue

import json

@easy_bot_command("addlistener", True)
def add_listeners(message, raw):
	try:
		listener_targets = json.load(open("listeners.json"))
		
	except (IOError, ValueError):
		listener_targets = {}

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
		
	open("listeners.json", "w").write(json.dumps(listener_targets, sort_keys=True, indent=4, separators=(',', ': ')))
		
	return ["Listener added succesfully!"]
	
@easy_bot_command("listlisteners")
def list_listeners(message, raw):
	if raw:
		return
		
	try:
		listener_targets = json.load(open("listeners.json"))
		
	except IOError:
		listener_targets = {}
		
	return "\x02Listener List:\x02 " + "; ".join("{} -> {}".format(x[0], ", ".join(x[1])) for x in listener_targets.items())
	
@easy_bot_command("removelistener", True)
def add_listeners(message, raw):
	try:
		listener_targets = json.load(open("listeners.json"))
		
	except (IOError, ValueError):
		listener_targets = {}

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
		
	open("listeners.json", "w").write(json.dumps(listener_targets, sort_keys=True, indent=4, separators=(',', ': ')))
		
	return ["Listener removed succesfully!"]

@easy_bot_command("reloadlisteners", True)
def reload_listeners(message, raw):
	if raw:
		return
		
	try:
		open("listeners.json", "w").write(json.dumps(json.loads(open("listeners.json").read()), sort_keys=True, indent=4, separators=(',', ': ')))
		
	except (IOError, ValueError):
		return "Error reloading listeners!"

	return "Success reloading listeners!"
	
@easy_bot_command("clearlisteners", True)
def clear_Listeners(message, raw):
	if raw:
		return
		
	open("listeners.json", "w").write("{}")
	
	return "Done clearing listeners!"
	
@bot_command("ListenerParse", False, True)
def listener_parsing(message, connector, index, raw):
	try:
		listener_targets = json.load(open("listeners.json"))
		
	except (IOError, ValueError):
		listener_targets = {}
		
	def message_target(idx, msg, target=None):
		if not target:
			target = get_message_target(connector, message, index)
			 
		connector.send_message(idx, target, msg)
	
	target_index = None

	try:
		if "{}:{}".format(connector.connections[index][6], message["channel"]).lower() in listener_targets.keys():
			for connection in connector.connections:
				for target in listener_targets["{}:{}".format(connector.connections[index][6], message["channel"]).lower()]:
					if target.startswith(connection[6] + ":"):
						real_target = target.split(":")[1]
					
						if message["type"] == "PRIVMSG":
							if not (message["message"].startswith("\x01ACTION") and message["message"].endswith("\x01")):
								message_target(connector.connections.index(connection), "[{}@{}] <{}> {}".format(message["channel"], connector.connections[index][6], message["nickname"], message["message"]),real_target)
								
							else:
								message_target(connector.connections.index(connection), "[{}@{}] * {} {}".format(message["channel"], connector.connections[index][6], message["nickname"], " ".join(message["arguments"][1:]))[:-1], real_target)
								
						else:
							message["ntype"] = message["raw"].split(" ")[1]
							message["nickname"] = message["raw"].split("!")[0]
							message["channel"] = message["raw"].split(" ")[2]
							
							if message["ntype"].lower() == "part":
								kick_reason = ":".join(message["raw"].split(":")[1:])
							
								message_target(connector.connections.index(connection), "[{}@{}] --- {} left (Reason: {})".format(message["channel"], connector.connections[index][6], message["nickname"], kick_reason), real_target)
								
							elif message["ntype"].lower() == "join":
								print "Yay join!"
							
								message_target(connector.connections.index(connection), "[{}@{}] +++ {} joined".format(message["channel"].strip(":"), connector.connections[index][6], message["nickname"]), real_target)
								
							elif message["ntype"].lower() == "kick":
								kick_target = message["raw"].split(" ")[3]
								kick_reason = ":".join(message["raw"].split(":")[1:])
							
								message_target(connector.connections.index(connection), "[{}@{}] @ {} kicked {} (Reason: {})".format(message["channel"], connector.connections[index][6], message["nickname"], kick_target, kick_reason), real_target)
								
							elif message["ntype"].lower() == "quit":
								kick_reason = ":".join(message["raw"].split(":")[1:])
							
								message_target(connector.connections.index(connection), "[{}@{}] # {} has quit (Reason: {})".format(message["channel"], connector.connections[index][6], message["nickname"], kick_reason), real_target)
							
	except KeyError:
		try:
			message["ntype"] = message["raw"].split(" ")[1]
			
		except IndexError:
			return
			
		message["nickname"] = message["raw"].split("!")[0]
		message["channel"] = message["raw"].split(" ")[2]
		
		if message["ntype"].lower() == "part":
			kick_reason = ":".join(message["raw"].split(":")[1:])
		
			message_target(connector.connections.index(connection), "[{}@{}] --- {} left (Reason: {})".format(message["channel"], connector.connections[index][6], message["nickname"], kick_reason), real_target)
			
		elif message["ntype"].lower() == "join":
			print "Yay join!"
		
			message_target(connector.connections.index(connection), "[{}@{}] +++ {} joined".format(message["channel"].strip(":"), connector.connections[index][6], message["nickname"]), real_target)
			
		elif message["ntype"].lower() == "kick":
			kick_target = message["raw"].split(" ")[3]
			kick_reason = ":".join(message["raw"].split(":")[1:])
		
			message_target(connector.connections.index(connection), "[{}@{}] @ {} kicked {} (Reason: {})".format(message["channel"], connector.connections[index][6], message["nickname"], kick_target, kick_reason), real_target)
			
		elif message["ntype"].lower() == "quit":
			kick_reason = ":".join(message["raw"].split(":")[1:])
		
			message_target(connector.connections.index(connection), "[{}@{}] # {} has quit (Reason: {})".format(message["channel"], connector.connections[index][6], message["nickname"], kick_reason), real_target)