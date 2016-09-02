import collections
import imp
import glob
import importlib
import os
import ntpath
import re
import json

commands = []
command_names = {}
plugins = {}
exempt_list = []
at_pload = {}
at_pexit = {}
current_plugin = ""
reloaded = False

def flatten(l):
    for el in l:
        if isinstance(el, collections.Iterable) and not isinstance(el, basestring):
            for sub in flatten(el):
                yield sub
        else:
            yield el

def get_message_target(connector, message, index):
	return (message["channel"] if message["channel"] != get_bot_nickname(connector, index) else message["nickname"])
								
def get_bot_nickname(connector, index):
	if connector.connections[index][4] == None:
		print "Name missing!"

	return connector.connections[index][4]
	
def fetch_name(filepath):
    return os.path.splitext(ntpath.basename(filepath))[0]
	
def reload_all_plugins():
	global commands
	global command_names
	global current_plugin
	global plugins
	global at_pexit
	global reloaded
	global at_pload
	
	print "Reloading plugins..."
	commands = []
	command_names = {}

	plugin_list = [fetch_name(module) for module in glob.glob("plugins/*.py") if os.path.isfile(module)]

	json.dump(plugin_list, open("pluginlist.json", "w"))
	
	for plugin in plugin_list:
		current_plugin = plugin
		print current_plugin
		plugins[plugin] = importlib.import_module("plugins." + plugin)
		
	commands = []
	command_names = {}
	
	for plugin, module in plugins.items():
		current_plugin = plugin
	
		imp.reload(module)
		
		print "Executing plugin exit functions..."
		for pexitlist in at_pexit.values():
			for func in pexitlist:
				print func.__name__
				func(reloaded)
		
		print "Executing function loading functions..."
		try:
			for func in at_pload[plugin]:
				func()
				
		except KeyError:
			pass
			
		at_pexit[plugin] = []
		at_pload[plugin] = []
		
	reloaded = True
		
	print "Plugins reloaded! ({})".format(command_names)
		
	return plugin_list

def at_plugin_reload(reload_only=False):
	def real_decorator(func):
		global at_pexit
		global current_plugin
		
		def wrapper(reloading):
			if not reload_only or not reloaded:
				func()
			
		try:
			at_pexit[current_plugin].append(wrapper)
		
		except KeyError:
			at_pexit[current_plugin] = [wrapper]
			
		except AttributeError:
			print at_pexit
			raise
			
		print at_pexit
		return wrapper
		
	return real_decorator
	
def at_plugin_load(func):
	global at_pload
	global current_plugin
	
	def wrapper():
		func()
		
	try:
		at_pload[current_plugin].append(func)
	
	except KeyError:
		at_pload[current_plugin] = [func]
		
	except AttributeErrorError:
		print at_pload
		raise
		
	return wrapper
	
def easy_bot_command(command_name=None, admin_command=False, all_messages=False, dont_parse_if_prefix=False, dont_show_in_list=False):
	def real_decorator(func):
		global commands
		global command_names
		
		current_plugin = get_current_plugin()

		def wrapper(message, connector, index, command_prefix, master):
			result = ""
		
			if not all_messages:
				if command_name == None:
					command_name_to_use = func.__name__

				else:
					command_name_to_use = command_name

				if message["type"] == "PRIVMSG":
					for hostmask in exempt_list:
						try:
							if re.match(hostmask, message["host"]):
								if (
										not admin_command or message["nickname"] == master
								) and (
										not dont_parse_if_prefix or not message["message"].startswith(command_prefix)
								) and not (
										message["nickname"] == message["channel"] == get_bot_nickname(connector, index)
								) and (
										not dont_parse_if_prefix and message["arguments"][0].lower() == (command_prefix + command_name_to_use).lower()
								):
									print "Exempted found!"
								return
									
						except re.error:
							pass
					
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
					result = func(message, True)
					
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
					
			try:
				if not result:
					return
					
			except UnboundLocalError:
				return
				
			if result.__class__.__name__ == "str":
				connector.send_message(index, get_message_target(connector, message, index), result)
			
			elif hasattr(result, "__iter__"):
				for output_message in flatten(result):
					connector.send_message(index, get_message_target(connector, message, index), output_message)
					
		commands.append(wrapper)
		
		if (not dont_parse_if_prefix and not all_messages) or dont_show_in_list:
			try:
				command_names[current_plugin].append(command_name)
				
			except KeyError:
				command_names[current_plugin] = [command_name]

		return wrapper

	return real_decorator


def bot_command(command_name=None, admin_command=False, all_messages=False, dont_parse_if_prefix=False, dont_show_in_list=False):
	global current_plugin

	def real_decorator(func):
		global commands
		global command_names

		def wrapper(message, connector, index, command_prefix, master):
			if not all_messages:
				if command_name == None:
					command_name_to_use = func.__name__

				else:
					command_name_to_use = command_name

				if message["type"] == "PRIVMSG":
					for hostmask in exempt_list:
						try:
							if re.match(hostmask, message["host"]):
								if (
										not admin_command or message["nickname"] == master
								) and (
										not dont_parse_if_prefix or not message["message"].startswith(command_prefix)
								) and not (
										message["nickname"] == message["channel"] == get_bot_nickname(connector, index)
								) and (
										not dont_parse_if_prefix and message["arguments"][0].lower() == (command_prefix + command_name_to_use).lower()
								):
									print "Exempted found!"
									
								return
								
						except re.error:
							pass
				
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
		
		if (not dont_parse_if_prefix and not all_messages) or dont_show_in_list:
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