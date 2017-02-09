import collections
import imp
import glob
import importlib
import os
import ntpath
import re
import json
import threading


connector_retrievers = []
commands = []
command_names = {}
plugins = {}
exempt_list = json.load(open("exempts.json"))
at_pload = {}
at_pexit = {}
current_plugin = ""
reloaded = False
connector = None


def threaded_function(daemon_thread=False):
	def __decorator__(func):
		def __wrapper__(*args, **kwargs):
			t = threading.Thread(
				target=func,
				args=args,
				kwargs=kwargs,
			)

			t.daemon = daemon_thread

			return t

		return __wrapper__

	return __decorator__

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

	print "Loading plugins: " + ", ".join(plugin_list)

	for plugin in plugin_list:
		print plugin + "...",
		plugins[plugin] = importlib.import_module("plugins." + plugin)
		print "done"

	commands = []
	command_names = {}

	for plugin, module in plugins.items():
		current_plugin = plugin

		print "Executing plugin exit functions..."
		for pexitlist in at_pexit.values():
			for func in pexitlist:
				print func.__name__
				func(reloaded)

		try:
			imp.reload(module)

		except ImportError:
			pass

		print "Executing function loading functions..."
		try:
			for func in at_pload[plugin]:
				func()

		except KeyError:
			pass

		at_pexit[plugin] = []
		at_pload[plugin] = []

	reloaded = True

	print "Plugins reloaded!"

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

				if message["type"].lower() == "privmsg":
					for hostmask in exempt_list:
						try:
							if re.match(hostmask, message["host"]):
								return

						except re.error:
							pass

					if (
							not admin_command or message["nickname"] == master or True in [re.match(h, message["host"]) != None for h in json.load(open("admins.json"))]
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
						not dont_parse_if_prefix or not message["message"].startswith(command_prefix)
					) and not (
						message["nickname"] == message["channel"] == get_bot_nickname(connector, index)
					) and (
						not dont_parse_if_prefix and message["arguments"][0].lower() == (command_prefix + command_name_to_use).lower()
					):
						result = "{}: Permission denied from executing command `{}`!".format(message["nickname"], command_name_to_use)

					if not (not dont_parse_if_prefix or not message["message"].startswith(command_prefix)):
						if command_name == None:
							command_name_to_use = func.__name__

						else:
							command_name_to_use = command_name

						print "Command {} couldn't run:".format(command_name_to_use)
						print "Admin certified:", not admin_command or message["nickname"] == master
						print "Don't-parse-if-prefix certified:", not dont_parse_if_prefix or not message["message"].startswith(command_prefix)
						print "Not self-sending-message certified:", not message["nickname"] == message["channel"] == get_bot_nickname(connector, index)

				else:
					result = func(message, True)

			else:
				if (not admin_command) or message["nickname"] == master or True in [re.match(h, message["host"]) != None for h in json.load(open("admins.json"))]:
					if message["type"].lower() == "privmsg":
						result = func(message, False)

					else:
						result = func(message, True)

				else:
					if command_name == None:
						command_name_to_use = func.__name__

					else:
						command_name_to_use = command_name

					if message["type"] == "privmsg":
						print "Command {} couldn't run for admin reasons.".format(command_name_to_use)

					else:
						result = func(message, True)

			try:
				if not result:
					return

			except UnboundLocalError:
				return

			if result.__class__.__name__ in ("str", "unicode"):
				print result

				connector.send_message(index, get_message_target(connector, message, index), result)

			elif hasattr(result, "__iter__"):
				for output_message in flatten(result):
					print output_message

					connector.send_message(index, get_message_target(connector, message, index), output_message)

		commands.append(wrapper)

		if (not dont_parse_if_prefix and not all_messages) or dont_show_in_list:
			try :
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

				if message["type"].lower() == "privmsg":
					for hostmask in exempt_list:
						try:
							if re.match(hostmask, message["host"]):
								return

						except re.error:
							pass

					if command_name == None:
						command_name_to_use = func.__name__

					else:
						command_name_to_use = command_name

					if (
						(not admin_command or message["nickname"] == master or True in [re.match(h, message["host"]) != None for h in json.load(open("admins.json"))]) and not
						(message["nickname"] == message["channel"] == get_bot_nickname(connector, index)) and
						(
							(
								dont_parse_if_prefix and
								not message["message"].startswith(command_prefix)
							) or
							(
								not dont_parse_if_prefix and
								message["arguments"][0] == command_prefix + command_name_to_use
							)
						)
					):
						print "Executing command!"
						func(message, connector, index, False)

					else:
						if (
							not (message["nickname"] == message["channel"] == get_bot_nickname(connector, index)) and
							(
								(
									dont_parse_if_prefix and
									not message["message"].startswith(command_prefix)
								) or
								(
									not dont_parse_if_prefix and
									message["arguments"][0] == command_prefix + command_name_to_use
								)
							)
						):
							connector.send_message(index, get_message_target(connector, message, index), "{}: Permission denied from executing command `{}`!".format(message["nickname"], command_name_to_use))
							print [(h, re.match(h, message["host"])) for h in json.load(open("admins.json"))]

					if not (not dont_parse_if_prefix or not message["message"].startswith(command_prefix)):
						print "Error: prefix found!"

				else:
					func(message, connector, index, True)

			else:
				try:
					if (not admin_command) or message["nickname"] == master or True in [re.match(h, message["host"]) != None for h in json.load(open("admins.json"))]:
						func(message, connector, index, False)

					else:
						if command_name == None:
							command_name_to_use = func.__name__

						else:
							command_name_to_use = command_name

						print "Command {} couldn't run for admin reasons.".format(command_name_to_use)


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

def connector_retriever(func):
	connector_retrievers.append(func)
	return func

def get_commands():
	return commands

def get_command_names():
	return command_names

def add_exempt(user):
	exempt_list.append(user)

	json.dump(exempt_list, open("exempts.json", "w"))

def remove_exempt(user):
	exempt_list.remove(user)

	json.dump(exempt_list, open("exempts.json", "w"))

def get_exempts():
	return exempt_list

def get_current_plugin():
	return current_plugin

def got_connector(d):
	for c in connector_retrievers:
		c(d)
