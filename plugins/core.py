import plugincon

from importlib import import_module
from plugincon import bot_command, easy_bot_command, get_message_target, get_bot_nickname, reload_all_plugins


@easy_bot_command("eval", True)
def evaluate_expression(message, raw):
	if not raw:
		return [str(eval(" ".join(message["arguments"][1:])))]
		
	else:
		return []
		
@easy_bot_command("hello")
def hello_there(message, raw):
	if not raw:
		return ["Hello, {}!".format(message["nickname"])]
		
	else:
		return []
		
@bot_command("commands")
def help_list(message, connector, index, raw):
	if raw:
		return
	
	def send_msg(mesg):
		print mesg
		connector.send_message(index, message["nickname"], mesg)
		
	def send_msgs(lst):
		for item in lst:
			send_msg(item)
		
	def msg(mesg):
		connector.send_message(index, get_message_target(connector, message, index), mesg)
		
	send_msgs(["\'{}\' plugin has the following commands -> ".format(plugin.decode("utf-8"))	 + ", ".join([x.decode("utf-8") for x in command_list]) for plugin, command_list in plugincon.get_command_names().items()])
		
	msg("Sent you help via PM.")
	return	
		
@bot_command("join", True)
def join_channel(message, connector, index, raw):
	if not raw:
		if len(message["arguments"]) < 2:
			connector.send_message(index, get_message_target(connector, message, index), "Join failed!")
		
		connector.send_command(index, "JOIN " + message["arguments"][1])
		
@bot_command("part", True)
def part_channel(message, connector, index, raw):
	if not raw:
		if len(message["arguments"]) < 2:
			connector.send_message(index, get_message_target(connector, message, index), "Part failed!")
		
		connector.send_command(index, "PART " + message["arguments"][1])
		
@bot_command("msg", True)
def part_channel(message, connector, index, raw):
	if not raw:
		if len(message["arguments"]) < 3:
			connector.send_message(index, get_message_target(mconnector, essage, index), "Message to channel failed!")
		
		connector.send_message(index, message["arguments"][1], " ".join(message["arguments"][2:]))
		
@bot_command("action", True)
def action(message, connector, index, raw):
	if not raw:
		if len(message["arguments"]) < 3:
			connector.send_message(index, get_message_target(connector, message, index), "Action to channel failed!")
			
		connector.send_message(index, message["arguments"][1], "\x01ACTION {}\x01".format(" ".join((message["arguments"][2:]))))
		
@easy_bot_command("reload", True)
def reload_plugins(message, raw):
	if not raw:
		return ["Reloaded following plugins: " + " ".join(reload_all_plugins())]
		
@bot_command("groupnick", True)
def group_nickname(message, connector, index, raw):
	if raw:
		return
		
	connector.send_message(index, "NickServ", "GROUP")
	
@easy_bot_command("addexempt", True)
def add_exempt(message, raw):
	if raw:
		return

	if len(message["arguments"]) < 2:
		return ["Syntax: addexempt <list of hostmasks>"]

	for hostmask in message["arguments"][1:]:
		plugincon.add_exempt(hostmask)
		
	return ["Hostmasks added succesfully: " + " ".join(message["arguments"][1:])]
	
@easy_bot_command("removeexempt", True)
def add_exempt(message, raw):
	if raw:
		return

	if len(message["arguments"]) < 2:
		return ["Syntax: removeexempt <list of hostmasks>"]

	for hostmask in message["arguments"][1:]:
		plugincon.remove_exempt(hostmask)
		
	return ["Hostmasks removed succesfully: " + " ".join(message["arguments"][1:])]
	
@easy_bot_command("listexempts")
def list_exempts(message, raw):
	if raw:
		return

	return ["Exempt list: " + " ".join(plugincon.get_exempts())]
	
@bot_command("kick")
def kick_user(message, connector, index, raw):
	if raw:
		return
		
	if len(message["arguments"]) < 2:
		connector.send_message(index, get_message_target(connector, message, index), "Not enough arguments!")
		
	connector.send_command(index, "KICK {} {} :{}".format(message["channel"], message["arguments"][1], " ".join()))
	
@bot_command("ban")
def ban_user(message, connector, index, raw):
	if raw:
		return
		
	if len(message["arguments"]) < 2:
		connector.send_message(index, get_message_target(connector, message, index), "Not enough arguments!")
		
	connector.send_command(index, "BAN {} {} :{}".format(message["channel"], message["arguments"][1], " ".join()))
	
@bot_command("kban")
def kickban_user(message, connector, index, raw):
	if raw:
		return
	
	if len(message["arguments"]) < 2:
		connector.send_message(index, get_message_target(connector, message, index), "Not enough arguments!")
		
	connector.send_command(index, "KICK {} {} :{}".format(message["channel"], message["arguments"][1], " ".join()))
	connector.send_command(index, "BAN {} {} :{}".format(message["channel"], message["arguments"][1], " ".join()))
	
@bot_command("invite")
def invite_user(message, connector, index, raw):
	if raw:
		return
		
	tgtchan = get_message_target(connector, message, index)
		
	if len(message["arguments"]) < 2:
		connector.send_message(index, tgtchan, "Syntax: invite <user>")
		return

	connector.send_command(index, "INVITE {} {}".format(message["arguments"][1], message["channel"]))