import plugincon

from importlib import import_module
from plugincon import bot_command, easy_bot_command


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
		
