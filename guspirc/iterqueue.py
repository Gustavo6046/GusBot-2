from Queue import Queue, Empty


class IterableQueue(Queue, object):
    def __init__(self):
        super(IterableQueue, self).__init__()
        self.past_items = []

    def __iter__(self):
        return self

    def empty(self):
        try:
            previous = self.get_nowait()

        except Empty:
            return True

        else:
            self.put_nowait(previous)
            return False

    def flush(self):
        while not self.empty:
            self.get_nowait()

    def set_to_iterator(self, iterator=(), flush_before_putting_iterator=False):
        if flush_before_putting_iterator:
            while not self.empty():
                self.get_nowait()

        for x in iterator:
            self.put_nowait(x)

        return self

    def __len__(self):

        if self.empty():
            return 0
        else:

            i = 0

            putback = []

            while not self.empty():
                x = self.get_nowait()
                putback.append(x)
                i += 1

            for x in putback:
                self.put_nowait(x)

            return i

    def next(self):
        try:
            x = self.get_nowait()
        except Empty:
            return None
        self.past_items.append(x)
        try:
            self.put(self.get())
        except Empty:
            self.close()
        return x

    def close(self, ):
        for x in self.past_items:
            self.put(x)
