from bot import connection
from sys import argv, exit as status_exit
from time import sleep
from threading import Thread
from functools import wraps

print "Loading INI {} for server configuration...".format(argv[1])

try:
    data = connection(["config/" + argv[1] + ".ini"])
    connector = data[0]
    command_prefix = data[1]
except IndexError:
    print "No argument given!"
    status_exit(3)

if connector is None:
    print "INI file given does not exist or is invalid!"
    status_exit(2)

server_connections = len(connector.connections)

commands = []


def easy_bot_command(command_name=None, admin_command=False):
    def real_decorator(func):
        global commands

        def wrapper(message, connector, index, command_prefix, master):
            print message

            try:
                if command_name == None:
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
                                "nickname"]), message_to_send)

            except KeyError:
                for message_to_send in func(message, True):
                    connector.send_command(index, message_to_send)

        commands.append(wrapper)

        return wrapper

    return real_decorator


def bot_command(command_name=None, admin_command=False):
    def real_decorator(func):
        global commands

        def wrapper(message, connector, index, command_prefix, master):
            print message
            print command_prefix + command_name

            try:
                if message["arguments"][0] == command_prefix + command_name and (
                            not admin_command or message["nick"] == master
                ):
                    func(message, connector, index, False)

            except KeyError:
                func(message, connector, index, True)

        commands.append(wrapper)

        return wrapper

    return real_decorator


from plugins import *


def server_loop(index):
    global connector, loaded_plugins

    while True:
        connector.main_loop(index)

        for message in connector.receive_all_messages(index):
            for plugin_function in commands:

                return_data = plugin_function(parse_message(message), connector, index, command_prefix,
                                              connector.connections[index][3])

                print "Plugin executed! Parsing return dict..."

                try:
                    for addition in return_data["addplugins"]:
                        print "Loading plugin {}...".format(addition.__name__)
                        loaded_plugins.remove(addition)
                        loaded_plugins.append(addition)

                    print "Plugins loaded succesfully!"

                except (KeyError, TypeError):
                    print "Nothing returned or invalid return type. In the first case, it's ok, " \
                          "in the second case, keep in mind that messages must be sent via " \
                          "connector.send_message(index, message[\"channel\", <message>) and not as a return value!"

        connector.relay_out_queue(index)


def parse_message(raw_message):
    message = ":".join(raw_message.split(":")[1:])
    try:
        return {
            "message": message,
            "nickname": message.split("!")[0], "ident": message.split("!")[1].split("@")[0],
            "hostname": message.split(" ")[0].split("@")[1], "type": message.split(" ")[1],
            "channel": message.split(" ")[2], "body": ":".join(message.split(":")[1:]),
            "arguments": ":".join(message.split(":")[1:]).split(" ")
        }
    except IndexError:
        return {
            "message": message
        }


print "Starting server threads!"
for x in xrange(server_connections):
    t = Thread(target=server_loop, args=(x,))
    t.daemon = True
    t.start()

while True:
    sleep(0.8)
