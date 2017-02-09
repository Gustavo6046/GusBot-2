import json
import sys
import time
import plugincon

from importlib import import_module
from glob import glob
from bot import connection
from sys import argv, exit as status_exit
from time import sleep
from threading import Thread
from functools import wraps

# Credits to Tobias Kienzler for his solution! http://stackoverflow.com/a/16589622/5129091
def full_stack():
    import traceback, sys
    exc = sys.exc_info()[0]
    stack = traceback.extract_stack()[:-1]  # last one would be full_stack()
    if not exc is None:  # i.e. if an exception is present
        del stack[-1]       # remove call of full_stack, the printed exception
                            # will contain the caught exception caller instead
    trc = 'Traceback (most recent call last):\n'
    stackstr = trc + ''.join(traceback.format_list(stack))
    if not exc is None:
         stackstr += '  ' + traceback.format_exc().lstrip(trc)
    return stackstr

error_log = "last_error.log"

def server_loop(index):
    global connector
    global error_log

    while True:
        connector.main_loop(index)

        for message in connector.receive_all_messages(index):
            message = message.encode("utf-8")

            parsed = parse_message_2(message)

            for plugin_function in plugincon.get_commands():
                try:
                    plugin_function(parsed, connector, index, command_prefix, connector.connections[index][3])

                except BaseException as plugin_error:
                    stack = full_stack()
                    print stack

                    elf = open(error_log, "w")

                    if parsed["type"].upper() == "PRIVMSG":
                        connector.send_message(index, parsed["channel"], "Error parsing command! ({}: {})".format(plugin_error.__class__.__name__, plugin_error))

                        elf.write(stack)

        connector.relay_out_queue(index)

        time.sleep(0.2)

class IRCMessage(object):
    def __init__(self, m):
        if type(m) == str:
            m = parse_message(m)

        self.raw_dict = m

        for k, v in m.iteritems():
            setattr(self, k, v)

    @classmethod
    def from_raw(cls, raw):
        return cls(parse_message(raw))

    def __getitem__(self, x):
        return self.raw_dict[x]

    def __setitem__(self, i, x):
        self.raw_dict[i] = x

def parse_message_2(raw_message):
    return IRCMessage(parse_message(raw_message))

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
            "host": message.split(" ")[0],
            "channel": message.split(" ")[2],
            "body": " ".join(":".join(message.split(":")[1:]).split(" ")[1:]),
            "arguments": ":".join(message.split(":")[1:]).split(" "),
        }

    except IndexError:
        return {
            "raw": message,
            "type": "",
        }

def run():
    global connector, command_prefix, master

    plugincon.reload_all_plugins()

    debug = False # change this in the source code upon finding any problem with exception that can't be traced!

    print "Loading INI {} for server configuration...".format(argv[1])

    try:
        connector, command_prefix, master = connection(["config/" + argv[1] + ".ini"])

    except IndexError:
        print "No argument given!"
        status_exit(3)

    except TypeError:
        print "INI file given does not exist or is invalid!"
        status_exit(2)

    if connector is None:
        print "INI file given does not exist or is invalid!"
        status_exit(2)

    plugincon.connector = connector

    server_connections = len(connector.connections)

    print "Starting server threads!"

    for x in xrange(server_connections):
        t = Thread(target=server_loop, args=(x,))
        t.daemon = True
        t.start()
        old_servers = connector.connections

    while True:
        sleep(0.8)

        if old_servers != connector.connections:
            for i, x in enumerate(connector.connections):
                if x not in old_servers:
                    print "Adding loop for server {}!".format(i)
                    t = Thread(target=server_loop, args=(i,))
                    t.daemon = True
                    t.start()

        old_servers = connector.connections

if __name__ == "__main__":
    run()
