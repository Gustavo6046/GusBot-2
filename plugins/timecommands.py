import time
import threading
import plugincon


def threaded_function(auto_start=True, daemon=False):
    def __decorator__(func):
        def __wrapper__(*args, **kwargs):
            t = threading.Thread(
                target=func,
                args=args,
                kwargs=kwargs
            )

            t.daemon = daemon

            if auto_start:
                t.start()

            return t

        return __wrapper__

    return __decorator__

class CommandTimer(object):
    def __init__(self, connector, message, index, raw, time=5, auto_execute=False, execution=None):
        # Configuration stuff
        self.time = time
        self.execution = execution
        self.executed = False

        # Command stuff
        self.message   = message
        self.index     = index
        self.connector = connector
        self.raw       = raw

        # Starting timer
        if auto_execute:
            self.thread = self.execute()

    @threaded_function(auto_start=True)
    def execute(self):
        time.sleep(self.time)

        self.executed = True
        if self.execution is not None:
            self.execution(self.message, self.connector, self.index, self.raw)

        self.end_timer()

    def end_timer(self):
        pass

    def send_message(self, message=""):
        self.connector.send_message(
            self.index,
            plugincon.get_message_target(self.connector, self.message, self.index),
            message
        )

class ConditionedCommand(CommandTimer):
    def __init__(self, connector, message, index, raw, condition_func, auto_execute=False, execution=None):
        super(ConditionedCommand, self).__init__(connector, message, index, raw, time=0, auto_execute=auto_execute, execution=execution)

        self.condition = condition_func

    @threaded_function(auto_start=True)
    def execute(self):
        while not self.condition(self):
            time.sleep(0.2)

        self.executed = True
        if self.execution is not None:
            self.execution(self.message, self.connector, self.index, self.raw)

        self.end_timer()
