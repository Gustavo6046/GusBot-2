commands = []
command_names = []

def get_message_target(connector, message, index):
	return (message["channel"] if message["channel"] != get_bot_nickname(connector, index) else message["nickname"])
								
def get_bot_nickname(connector, index):
	if connector.connections[index][4] == None:
		print "Name missing!"

	return connector.connections[index][4]

def easy_bot_command(command_name=None, admin_command=False, all_messages=False, dont_parse_if_prefix=False):
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
					
				print get_bot_nickname(connector, index)

				if message["type"] == "PRIVMSG":
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
						
					else:
						print "Command couldn't run:"
						print "Admin certified:", not admin_command or message["nickname"] == master
						print "Don't-parse-if-prefix certified:", not dont_parse_if_prefix or not message["message"].startswith(command_prefix)
						print "Not self-sending-message certified:", not message["nickname"] == message["channel"] == get_bot_nickname(connector, index)
						print "Matching command:", not dont_parse_if_prefix and message["arguments"][0].lower() == (command_prefix + command_name_to_use).lower()
						return
						
					if not (not dont_parse_if_prefix or not message["message"].startswith(command_prefix)):
						print "Error: prefix found!"
						return

				else:
					print "Executing command! (raw)"
					result = func(message, True)
					
				if not result:
					return
					
				if isinstance(result, str):
					connector.send_message(index, get_message_target(connector, message, index), result)
				
				else:
					for output_message in result:
						connector.send_message(index, get_message_target(connector, message, index), output_message)
					
			else:
				try:
					if not admin_command or message["nick"] == master:
						func(message, False)
					
				except KeyError:
					func(message, True)

		commands.append(wrapper)
		command_names.append(command_name)

		return wrapper

	return real_decorator


def bot_command(command_name=None, admin_command=False, all_messages=False, dont_parse_if_prefix=False):
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
					
				print get_bot_nickname(connector, index)
				print master

				if message["type"] == "PRIVMSG":
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
						print "Command couldn't run:"
						print "Admin certified:", not admin_command or message["nickname"] == master
						print "Don't-parse-if-prefix certified:", not dont_parse_if_prefix or not message["message"].startswith(command_prefix)
						print "Not self-sending-message certified:", not message["nickname"] == message["channel"] == get_bot_nickname(connector, index)
						print "Matching command:", not dont_parse_if_prefix and message["arguments"][0].lower() == (command_prefix + command_name_to_use).lower()
						
					if not (not dont_parse_if_prefix or not message["message"].startswith(command_prefix)):
						print "Error: prefix found!"

				else:
					print "Executing command! (raw)"
					func(message, connector, index, True)
					
			else:
				try:
					print "..."
					if not admin_command or message["nick"] == master:
						func(message, connector, index, False)
					
				except KeyError:
					print "..."
					func(message, connector, index, True)

		commands.append(wrapper)
		command_names.append(command_name)

		return wrapper

	return real_decorator

def get_commands():
	return commands
	
def get_command_names():
	return command_names