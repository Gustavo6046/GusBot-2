import plugincon
import guspirc
import subprocess
import StringIO
import operator
import json
import main

from importlib import import_module
from plugincon import bot_command, easy_bot_command, get_message_target, get_bot_nickname, reload_all_plugins

@easy_bot_command("addserv", True)
def add_server(message, raw):
	if raw:
		return

	try:
		main.connector.add_connection_socket(message["arguments"][1], message["arguments"][2], message["arguments"][3], "A GusPIRC Bot", message["arguments"][4], message["arguments"][5], "email@address.com", "GusBot", True, message["arguments"][6:], use_ssl=False, master=main.master)

	except IndexError:
		return "Syntax: addserv <server address> <port> <ident> <nickname> <password> <autojoin channel [channel [...]]>"

	# server,
	# port=6697,
	# ident="GusPIRC",
	# real_name="A GusPIRC Bot",
	# nickname="GusPIRC Bot",
	# password="",
	# email="email@address.com",
	# account_name="",
	# has_account=False,
	# channels=None,
	# auth_numeric=267,
	# use_ssl=True,
	# master=""

	return "Server added succesfully!"

@easy_bot_command("shell", True)
def shell_exec(message, raw):
	if raw:
		return

	if len(message["arguments"]) < 2:
		return "Syntax: shell <command-line>"

	print "Executing: \'{}\'".format(" ".join(message["arguments"][1:]))

	# Calling shell and processing STDOUT
	sh = subprocess.Popen(message["arguments"][1:], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE, shell=True)
	input = our_stdin.getvalue()
	print "->> " + input
	output, err = sh.communicate(input)
	out = map(lambda x: x if x != "" else " ", output.split("\n"))

	print our_stdin.__dict__
	our_stdin.flush()

	try:
		return map(lambda x: x.strip("\r").encode("utf-8"), out)

	except UnicodeDecodeError:
		return map(lambda x: x.strip("\r"), out)

current_shell = None

@easy_bot_command("sh_init", True)
def start_shell_context(message, raw):
	if raw:
		return

	if len(message["arguments"]) < 2:
		return "@Syntax: sh_init <command-line>"

	print "Executing: \'{}\'".format(" ".join(message["arguments"][1:]))
	current_shell = subprocess.Popen(message["arguments"][1:], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE, shell=True)

	return iter(current_shell.stdout.readline, "")

@easy_bot_command("sh_feed", True)
def feed_shell_context(message, raw):
	if raw:
		return

	if len(message["arguments"]) < 2:
		return "@Syntax: sh_feed <stdin>"

	current_shell.stdin.write(" ".join(message["arguments"][1:]) + "\n")

	return iter(current_shell.stdout.readline, "")

@easy_bot_command("sh_stop", True)
def stop_shell_context(message, raw):
	if raw:
		return

	current_shell.terminate()

	return "@Shell program terminated succesfully!"

@bot_command("flushq", True)
def flush_out_queue(message, connector, index, raw):
	if raw:
		return

	connector.connections[index][2] = guspirc.iterqueue.IterableQueue()

	connector.send_notice(index, message["nickname"], "Queue flushed with success!")

@easy_bot_command("eval", True)
def evaluate_expression(message, raw):
	if raw:
		return

	r = u"Result | {}".format(unicode(eval(message["body"]))).encode("utf-8")
	print r
	return r

@easy_bot_command("exec", True)
def evaluate_statement(message, raw):
	if raw:
		return

	exec(" ".join(message["arguments"][1:]))

	return "Statement executed succesfully!"

@easy_bot_command("plugins")
def plugin_cmd_list(message, raw):
	if raw:
		return

	return "Plugins available: " + ", ".join(plugincon.plugins.keys())

@easy_bot_command("list")
def plugin_cmd_list(message, raw):
	if raw:
		return

	if len(message["arguments"]) < 2:
		return ["Syntax: ||list <plugin name>", "For a list of plugins use ||plugins"]

	return "Commands in plugin {}: {}".format(message["arguments"][1], ", ".join([x.encode("utf-8") for x in plugincon.command_names[message["arguments"][1]]]))

@bot_command("join", True)
def join_channel(message, connector, index, raw):
	if not raw:
		if len(message["arguments"]) < 2:
			connector.send_message(index, get_message_target(connector, message, index), "Join failed!")

		connector.send_command(index, "JOIN " + message["arguments"][1])

@bot_command("cmd", True)
def send_command_to_server(message, connector, index, raw):
	if raw:
		return

	if len(message["arguments"][1:]) < 2:
		connector.send_message(index, get_message_target(connector, message, index), "Syntax: cmd <command to send>")

	connector.send_command(index, " ".join(message["arguments"][1:]))

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

@bot_command("kick", True)
def kick_user(message, connector, index, raw):
	if raw:
		return

	if len(message["arguments"]) < 2:
		connector.send_message(index, get_message_target(connector, message, index), "Not enough arguments!")

	connector.send_command(index, "KICK {} {} :{}".format(message["channel"], message["arguments"][1], " ".join(message["arguments"][2:])))

@bot_command("ban", True)
def ban_user(message, connector, index, raw):
	if raw:
		return

	if len(message["arguments"]) < 2:
		connector.send_message(index, get_message_target(connector, message, index), "Not enough arguments!")

	connector.send_command(index, "BAN {} {} :{}".format(message["channel"], message["arguments"][1], " ".join(message["arguments"][2:])))

@bot_command("kban", True)
def kickban_user(message, connector, index, raw):
	if raw:
		return

	if len(message["arguments"]) < 2:
		connector.send_message(index, get_message_target(connector, message, index), "Not enough arguments!")

	connector.send_command(index, "KICK {} {} :{}".format(message["channel"], message["arguments"][1], " ".join(message["arguments"][2:])))
	connector.send_command(index, "BAN {} {} :{}".format(message["channel"], message["arguments"][1], " ".join(message["arguments"][2:])))

@bot_command("invite")
def invite_user(message, connector, index, raw):
	if raw:
		return

	tgtchan = get_message_target(connector, message, index)

	if len(message["arguments"]) < 2:
		connector.send_message(index, tgtchan, "Syntax: invite <user>")
		return

	connector.send_command(index, "INVITE {} {}".format(message["arguments"][1], message["channel"]))

@easy_bot_command("num_commands")
def number_of_commands(message, raw):
	if raw:
		return

	return "Number of Commands: {}".format(len(plugincon.get_commands()))

@easy_bot_command("addadmin", True)
def add_admin(message, raw):
	if raw:
		return

	r = json.dumps(json.load(open("admins.json")) + [message["body"]])
	open("admins.json", "w").write(r)

	return "Admin added succesfully!"

@easy_bot_command("remadmin", True)
def add_admin(message, raw):
	if raw:
		return

	r = json.load(open("admins.json"))
	r.remove(message["body"])
	open("admins.json", "w").write(json.dumps(r))

	return "Admin removed succesfully!"

@easy_bot_command("adminlist")
def list_admins(message, raw):
	if raw:
		return

	return "Admins (other than master): " + ", ".join("\'{}\'".format(a) for a in json.load(open("admins.json")))
