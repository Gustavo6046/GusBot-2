import glob
import time
import plugincon
import timecommands
import cson
import os


def message(message, connector, index, out):
    return connector.send_message(
        index,
        plugincon.get_message_target(connector, message, index),
        out
    )

notes = []

class Reminder(timecommands.CommandTimer):
    def __init__(self, connector, message, index, raw, time, output, auto_execute=False, execution=None):
        timecommands.CommandTimer.__init__(self, connector, message, index, raw, time=time, auto_execute=auto_execute, execution=execution)
        self.output = output

    def end_timer(self):
        self.send_message(self.output)

class Note(object):
    def __init__(self, message, connector, index, out, target):
        self.joined    = False
        self.sent      = False

        self.message   = message
        self.connector = connector
        self.index     = index
        self.out       = out

        self.target    = target

        self.detect_joined = plugincon.bot_command("__DETECT_JOINED__", all_messages=True, dont_show_in_list=True)(self.detect_joined)

        self.sender    = timecommands.ConditionedCommand(connector, message, index, False, self.join_check, True, self.send)

        self.save_time = time.time()
        self.save_str = "notes/{}-{}-{}.cson".format(message["nickname"], target, self.save_time)
        self.save(self.save_str)

    def send(self, message, connector, index, raw):
        time.sleep(0.1)

        globals()["message"](self.message, self.connector, self.index, self.out)

        self.sent = True

        del self

    def join_check(self, sender):
        return self.joined

    def save(self, filename):
        open(filename, "w").write(cson.dumps({
            "message": self.message.raw_dict,
            "index": self.index,
            "output": self.out,
            "target": self.target,
        }))

    @classmethod
    def from_dict(cls, dictionary, connector):
        return cls(dictionary["message"], connector, dictionary["index"], dictionary["output"], dictionary["target"])

    def detect_joined(self, message, connector, index, raw):
        data = message["raw"].split(" ")

        try:
            if data[1].upper() == "JOIN" and data[0].split("!")[0].lower() == self.target.lower():
                self.joined = True

        except IndexError:
            pass

    def __del__(self):
        if self.sent:
            os.remove(self.save_str)

@plugincon.bot_command("remind")
def remind_someone(message, connector, index, raw):
    if raw:
        return

    print message["arguments"]

    if len(message["arguments"]) < 3:
        globals()["message"](message, connector, index, "Syntax: remind [target=<target>] (timer|time)=<timer> <message>")
        return

    timed  = False
    target = None
    time   = None

    for i, a in enumerate(message["arguments"][1:3]):
        if a.startswith("timer=") or a.startswith("time="):
            time = float(a[6:])

        elif a.startswith("target="):
            target = a[7:]

    if not time:
        globals()["message"](message, connector, index, "Error: MUST specify timer!")
        return

    if not target:
        target = message["nickname"]

    msg_start = 2
    if message["arguments"][2].startswith("timer=") or message["arguments"][2].startswith("target="):
        msg_start = 3

    output = " ".join(message["arguments"][msg_start:])

    remind = Reminder(connector, message, index, False, time, "{}: {}".format(target, output), True)
    globals()["message"](message, connector, index, "Remind sent succesfully!")

@plugincon.bot_command("note")
def note_to_someone(message, connector, index, raw):
    if raw:
        return

    if len(message["arguments"]) < 2:
        globals()["message"](message, connector, index, "Syntax: note <target> <message>")
        return

    target = message["arguments"][1]
    output = " ".join(message["arguments"][2:])

    notes.append(Note(message, connector, index, "{}: {}".format(target, output), target))
    globals()["message"](message, connector, index, "Note sent succesfully!")

@plugincon.connector_retriever
def load_notes(connector):
    for note in glob.glob("notes/*.cson"):
        notes.append(Note.from_dict(cson.load(open(note)), plugincon.connector))
