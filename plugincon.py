commands = []
command_names = []

def easy_bot_command(command_name=None, admin_command=False):
	def real_decorator(func):
		global commands
		global command_names

		def wrapper(message, connector, index, command_prefix, master):
			print message

			try:
				if command_name is None:
					command_name_to_use = func.__name__
				else:
					command_name_to_use = command_name

				print command_prefix + command_name_to_use

				if message["arguments"][0] == command_prefix + command_name_to_use and (
						not admin_command or message["nick"] == master
				):
					for message_to_send in func(message, False):
						connector.send_message(index, (
							message["channel"] if message["channel"] != connector.connections[index][4] else message[
								"nickname"]), str(message_to_send))
								
				elif message["nick"] != master and admin_command:
					connector.send_message(index, (
							message["channel"] if message["channel"] != connector.connections[index][4] else message[
								"nickname"]), "Only the master specified in configuration file can operate this command!")
								
					print "{} != {} as master".format(master, message["nick"])

			except KeyError:
				for message_to_send in func(message, True):
					connector.send_command(index, message_to_send)

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
				print message
				print command_prefix + command_name

				if command_name == None:
					command_name_to_use = func.__name__

				else:
					command_name_to_use = command_name

				try:
					if (
							not admin_command or message["nick"] == master
					) and (
							not dont_parse_if_prefix or message["arguments"][0] == command_prefix + command_name_to_use
					):
						func(message, connector, index, False)
						
					if not (not dont_parse_if_prefix or message["arguments"][0] == command_prefix + command_name_to_use):
						print "Error: prefix found!"

				except KeyError:
					func(message, connector, index, True)
					
			else:
				try:
					if not admin_command or message["nick"] == master:
						func(message, connector, index, False)
					
				except KeyError:
					func(message, connector, index, True)

		commands.append(wrapper)
		command_names.append(command_name)

		return wrapper

	return real_decorator

def get_commands():
	return commands
	
def get_command_names():
	return command_names