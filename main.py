import json
import sys
import plugincon

from importlib import import_module
from glob import glob
from bot import connection
from sys import argv, exit as status_exit
from time import sleep
from threading import Thread
from functools import wraps

plugincon.reload_all_plugins()

debug = False # change this upon finding any problem with exception that can't be traced!

print "Loading INI {} for server configuration...".format(argv[1])

try:
	data = connection(["config/" + argv[1] + ".ini"])
	connector = data[0]
	command_prefix = data[1]
	
except IndexError:
	print "No argument given!"
	status_exit(3)

except TypeError:
	print "INI file given does not exist or is invalid!"
	status_exit(2)

if connector is None:
	print "INI file given does not exist or is invalid!"
	status_exit(2)

server_connections = len(connector.connections)
	
def server_loop(index):
	global connector

	while True:
		connector.main_loop(index)

		for message in connector.receive_all_messages(index):
			message = message.encode("utf-8")
		
			for plugin_function in plugincon.get_commands():
				try:
					plugin_function(parse_message(message), connector, index, command_prefix,
												  connector.connections[index][3])
												  
				except BaseException as plugin_error:
					print "Error parsing command! ({}: {})".format(plugin_error.__class__.__name__, plugin_error)
					
					if parse_message(message)["type"] == "PRIVMSG":
						connector.send_message(index, parse_message(message)["channel"], "Error parsing command! ({}: {})".format(plugin_error.__class__.__name__, plugin_error))
						
					if debug:
						raise

		connector.relay_out_queue(index)


def parse_message(raw_message):
	message = ":".join(raw_message.split(":")[1:])
	
	try:
		return {
			"raw": message,
			"type": "privmsg",
			"message": ":".join(message.split(":")[1:]),
			"nickname": message.split("!")[0],
			"ident": message.split("!")[1].split("@")[0],
			"hostname": message.split(" ")[0].split("@")[1], "type": message.split(" ")[1],
			"channel": message.split(" ")[2],
			"body": ":".join(message.split(":")[1:]),
			"arguments": ":".join(message.split(":")[1:]).split(" "),
		}
		
	except IndexError:
		return {
			"raw": message,
			"type": None,
		}


print "Starting server threads!"
for x in xrange(server_connections):
	t = Thread(target=server_loop, args=(x,))
	t.daemon = True
	t.start()

while True:
	sleep(0.8)
