from bot import connection
from sys import argv, exit as status_exit
from threading import Thread
import plugins

loaded_plugins = [plugins.core]
print "Loading INI {} for server configuration...".format(argv[1])

try:
    connector = connection(["config/" + argv[1] + ".ini"])
except IndexError:
    print "No argument given!"
    status_exit(3)

if connector is None:
    print "INI file given does not exist or is invalid!"
    status_exit(2)

server_connections = len(connector.connections)


def server_loop(index):
    global connector, loaded_plugins

    while True:
        print ""

        connector.main_loop(index)

        for message in connector.receive_all_messages(index):
            for plugin in loaded_plugins:
                for plugin_function in plugin.register_plugin():

                        data = plugin_function(parse_message(message), connector, index, loaded_plugins, "}:", connector.connections[index][3])

                        try:
                            for x in data["addplugins"]:
                                print "Loading plugin {}...".format(x)
                                loaded_plugins.remove(x)
                                loaded_plugins.append(x)

                            print "Plugins loaded succesfully!"

                        except (KeyError, TypeError):
                            pass

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
    Thread(target=server_loop, args=(x,)).start()
