import plugincon

from importlib import import_module
from plugincon import bot_command, easy_bot_command, get_message_target, get_bot_nickname


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
		
@easy_bot_command("commands")
def help_list(message, raw):
	if not raw:
		return ["Commands: " + " ".join([command for command in plugincon.get_command_names() if command != None])]
		
	else:
		return []
		
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