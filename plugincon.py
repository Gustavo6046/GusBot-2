import glob
import importlib
import os
import ntpath
import fnmatch
import json

commands = []
command_names = {}
plugins = {}
exempt_list = []
current_plugin = ""

def get_message_target(connector, message, index):
	return (message["channel"] if message["channel"] != get_bot_nickname(connector, index) else message["nickname"])
								
def get_bot_nickname(connector, index):
	if connector.connections[index][4] == None:
		print "Name missing!"

	return connector.connections[index][4]
	
def fetch_name(filepath):
    return os.path.splitext(ntpath.basename(filepath))[0]
	
def reload_all_plugins():
	print "Reloading plugins..."
	commands = []
	command_names = {}

	plugin_list = [fetch_name(module) for module in glob.glob("plugins/*.py") if os.path.isfile(module)]

	json.dump(plugin_list, open("pluginlist.json", "w"))
	
	for plugin in plugin_list:
		current_plugin = plugin
		print current_plugin
		plugins[plugin] = importlib.import_module("plugins." + plugin)
		
	print "Plugins reloaded! ({})".format(command_names)
		
	return plugin_list

def easy_bot_command(command_name=None, admin_command=False, all_messages=False, dont_parse_if_prefix=False):
	def real_decorator(func):
		global commands
		global command_names
		
		current_plugin = get_current_plugin()

		def wrapper(message, connector, index, command_prefix, master):
			if not all_messages:
				if command_name == None:
					command_name_to_use = func.__name__

				else:
					command_name_to_use = command_name

				if message["type"] == "PRIVMSG":
					for hostmask in exempt_list:
						if fnmatch.fnmatch(message["host"], hostmask):
							connector.send_message(index, get_message_target(connector, message, index), "You are exempted from using commands!")
							return
				
					if (
							not admin_command or message["nickname"] == master
					) and (
							not dont_parse_if_prefix or not message["message"].startswith(command_prefix)
					) and not (
							message["nickname"] == message["channel"] == get_bot_nickname(connector, index)
					) and (
							not dont_parse_if_prefix and message["arguments"][0].lower() == (command_prefix + command_name_to_use).lower()
					):
						print "Executing command!"
						result = func(message, False)
						
					elif (
							not (not admin_command or message["nickname"] == master)
					) and (
							not dont_parse_if_prefix or not message["message"].startswith(command_prefix)
					) and not (
							message["nickname"] == message["channel"] == get_bot_nickname(connector, index)
					) and (
							not dont_parse_if_prefix and message["arguments"][0].lower() == (command_prefix + command_name_to_use).lower()
					):
						result = "{}: Permission Denied!".format(message["nickname"])
						
					if not (not dont_parse_if_prefix or not message["message"].startswith(command_prefix)):
						print "Error: prefix found!"
						return

				else:
					print "Executing command! (raw)"
					result = func(message, True)
					
				try:
					if not result:
						return
						
				except UnboundLocalError:
					return
					
				if isinstance(result, str):
					connector.send_message(index, get_message_target(connector, message, index), result)
				
				else:
					for output_message in result:
						connector.send_message(index, get_message_target(connector, message, index), output_message)
					
			else:
				try:
					if (
						not admin_command or message["nick"] == master
					) and (
						not dont_parse_if_prefix or not message["message"].startswith(command_prefix)
					):
						result = func(message, False)
					
				except KeyError:
					result = func(message, True)
					
				if not result:
					return
					
				if isinstance(result, str):
					connector.send_message(index, get_message_target(connector, message, index), result)
				
				else:
					for output_message in result:
						connector.send_message(index, get_message_target(connector, message, index), output_message)
					
		commands.append(wrapper)
		
		if not dont_parse_if_prefix and not all_messages:
			try:
				command_names[current_plugin].append(command_name)
				
			except KeyError:
				command_names[current_plugin] = [command_name]

		return wrapper

	return real_decorator


def bot_command(command_name=None, admin_command=False, all_messages=False, dont_parse_if_prefix=False):
	global current_plugin

	def real_decorator(func):
		global commands
		global command_names

		def wrapper(message, connector, index, command_prefix, master):
			if not all_messages:
				print message["raw"]
				print command_prefix + command_name

				if command_name == None:
					command_name_to_use = func.__name__

				else:
					command_name_to_use = command_name

				if message["type"] == "PRIVMSG":
					for hostmask in exempt_list:
						if fnmatch.fnmatch(message["host"], hostmask):
							connector.send_message(index, get_message_target(connector, message, index), "You are exempted from using commands!")
							return
				
					if (
							not admin_command or message["nickname"] == master
					) and (
							not dont_parse_if_prefix or not message["message"].startswith(command_prefix)
					) and not (
							message["nickname"] == message["channel"] == get_bot_nickname(connector, index)
					) and (
							not dont_parse_if_prefix and message["arguments"][0].lower() == (command_prefix + command_name_to_use).lower()
					):
						print "Executing command!"
						func(message, connector, index, False)

						
					else:
						if (
							not (not admin_command or message["nickname"] == master)
							and (not dont_parse_if_prefix or not message["message"].startswith(command_prefix))
							and (not message["nickname"] == message["channel"] == get_bot_nickname(connector, index))
							and (not dont_parse_if_prefix and message["arguments"][0].lower() == (command_prefix + command_name_to_use).lower())
						):
							connector.send_message(index, get_message_target(connector, message, index), "{}: Permission Denied!".format(message["nickname"]))
						
					if not (not dont_parse_if_prefix or not message["message"].startswith(command_prefix)):
						print "Error: prefix found!"

				else:
					print "Executing command! (raw)"
					func(message, connector, index, True)
					
			else:
				try:
					if (
						not admin_command or message["nick"] == master
					) and (
						not dont_parse_if_prefix or not message["message"].startswith(command_prefix)
					):
						func(message, connector, index, False)
						
					else:		
						print "Command couldn't run:"
						print "Admin certified:", not admin_command or message["nickname"] == master
						print "Don't-parse-if-prefix certified:", not dont_parse_if_prefix or not message["message"].startswith(command_prefix)
						print "Not self-sending-message certified:", not message["nickname"] == message["channel"] == get_bot_nickname(connector, index)
						
					
				except KeyError:
					func(message, connector, index, True)

		commands.append(wrapper)
		
		if not dont_parse_if_prefix and not all_messages:
			try:
				command_names[current_plugin].append(command_name)
				
			except KeyError:
				command_names[current_plugin] = [command_name]

		return wrapper

	return real_decorator

def get_commands():
	return commands
	
def get_command_names():
	return command_names
	
def add_exempt(user):
	exempt_list.append(user)
	
def remove_exempt(user):
	exempt_list.remove(user)
	
def get_exempts():
	return exempt_list
	
def get_current_plugin():
	return current_plugin