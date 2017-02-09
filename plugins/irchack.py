about = """
          ^
         / \\
        /   \\
       /     \\
      /       \\
     /         \\
    /           \\
    | IRC Hack  |
    |           |
    |           |
    |           |
    | A game by |
    | Gustavo   |
    | Ramos     |
    | Rehermann |
-~=<=============>=~-
       \\6046|/
        |6046
        6046|
        |6046

A MUD-like IRC game about
exploring, non-Euclidean
rooms, corridors and reaching
downstairs for the next level
(a rather rogue one).

Encountering monsters, destroying
the Seal of Yendor and bringing
back the salvation for the entire
Upperland!

And then, in Chapter 2, sealing
Gehennom as you accidentally opened
it for the Amulet.

Chapter 3 COMING SOON!

I accept storyboard donations for
the Chapter 3: Upperland Community
at the following e-mail:

gugurehermann@gmail.com
"""
about.strip("\n")

import plugincon
import numpy
import random
import gamethinker
import wordgen
import pylab as plt
import multiprocessing

class SequentialDict(object):
    def __init__(self, x=[]):
        self._keys = [x[0] for y in x]
        self._values = [x[1] for y in x]

    @classmethod
    def from_pairs(cls, key, value):
        return cls(zip(key, value))

    @classmethod
    def fill(cls, key, value, size):
        return cls(((key, value),) * size)

    @classmethod
    def empty(cls):
        return cls([])

    def __iter__(self):
        return self.keys()

    def has_value(self, value):
        return value in self.values()

    def keys(self):
        return self._keys

    def insert(self, key, value, index=0):
        self._keys.insert(index, key)
        self._values.insert(index, value)

    def __setitem__(self, key, value):
        self._keys.append(key)
        self._values.append(value)

    def __getitem__(self, key):
        if type(key) is int:
            return self._values[key]

        else:
            for k, v in zip(self._keys, self._values):
                if k == key:
                    return v

            raise KeyError("Key '{}' not found in this SequentialDict!\nKeys available: {}{}\nAccess the SequentialDict's keys() function for more.".format(
                key,
                ", ".join(repr(x) for x in self._values[:9]),
                ("..." if len(self._values) > 9 else "")
            ))

    def __add__(self, other):
        if type(other) is dict or issubclass(type(other), dict):
            self._keys.extend(other.keys())
            self._values.extend(other.values())

            return self

        raise ValueError("{} must be a dict-like class!".format(other))

    def __sub__(self, other):
        if type(other) is dict or issubclass(type(other), dict):
            self._keys = list(other.keys() + self._keys)
            self._values = list(other.values() + self._values)

            return self

        raise ValueError("{} must be a dict-like class!".format(other))

    def extend(self, other):
        self += other
        return self

    def items(self):
        return zip(self.keys(), self.values())

def start_chunk(other_room):
    def __wrapper__(x, y, z):
        return Chunk(other_room)

    return __wrapper__

class Room(object):
    def __init__(self, game, level):
        self.light = random.random()
        self.chunks = numpy.array([[[Chunk(game, level, self) for _ in xrange(2)] for _ in xrange(2)] for _ in xrange(1)])
        self.name = wordgen.gen_word(1, 4)
        self.links = []
        self.all_stuff = []
        self.game = game
        self.level = level

        for a, x in enumerate(list(self.chunks)):
            for b, y in enumerate(x):
                for c, z in enumerate(y):
                    if z.objects != []:
                        for o in z.objects:
                            if o.visible(self.light):
                                self.all_stuff.append((o.description(), str("{}, {}, {}".format(a, b, c))))

        if not self.all_stuff:
            self.all_stuff = [["nothing", ""]]

        self.descriptor =\
        "This is a {} room. Somehow your brain associates it with the name {}. You see {} in here. There are {} corridors: {}.".format(
            self.game.light_descriptors[int(self.light * len(self.game.light_descriptors) - 1)],
            self.name,
            ", ".join(["{} {}".format(v, k) for k, v in self.all_stuff]),
            len(self.links),
            ", ".join([x.name for x in self.links])
        )

        if game.starting_chunk is None:
            game.starting_chunk = random.sample(self.chunks, 1)[0]

    def new_link(self, link):
        self.descriptor =\
        "This is a {} room. Somehow your brain associates it with the name {}. You see {} in here. There are {} corridors: {}.".format(
            self.game.light_descriptors[int(self.light * len(self.game.light_descriptors) - 1)],
            self.name,
            ", ".join(["{} {}".format(v, k) for k, v in self.all_stuff]),
            len(self.links),
            ", ".join([x.name for x in self.links])
        )

class GlobalRoom(Room):
    def __init__(self, game, level):
        self.game = game
        self.level = level
        self.chunks = []
        self.name = "Dungeons of Doom"
        self.light = random.uniform(0.075, 0.5)
        self.descriptor =\
        "This is a {} corridor.".format(self.game.light_descriptors[int(self.light * len(self.game.light_descriptors) - 1)])

class Chunk(object):
    def __init__(self, game, level, parent_room=None):
        self.parent_room = parent_room
        if not parent_room:
            self.parent_room = level.global_room

        self.objects = list()
        self.game = game
        self.level = level

        for o, c in game.generation_chance.items():
            if c > random.uniform(0, 100):
                self.objects.append(o(game, self, level))

        self.stuff = ", ".join([str(o.description()) for o in self.objects if o.visible(self.parent_room.light)])

        if not self.stuff:
            self.stuff = "nothing"

        self.descriptor = "You see {} here.".format(self.stuff)

    def step_into(self, other):
        for o in self.objects:
            o.chunk_step(other)

class Corridor(Chunk):
    def __init__(self, game, level, rooms):
        Chunk.__init__(self, game, level)
        self.game = game
        self.level = level
        self.name = wordgen.gen_word(1, 4)
        self.connected_rooms = rooms
        self.parent_room.chunks.append(self)

        for r in rooms:
            r.links.append(self)

            r.new_link(self)

class ChunkObject(object):
    description = "a rather generic object"

    def __init__(self, game, chunk, level):
        self.game = game
        self.chunk = chunk
        self.level = level

    def description(self):
        return type(self).description

    def chunk_step(self, stepper):
        pass

    def turn(self):
        pass

    def visible(self, light):
        return light > 0.3

    def use(self, stepper):
        pass

class Downstairs(ChunkObject):
    chance = 9

    def __init__(self, game, chunk, level):
        level.downstairs.append(self)

    def use(self, stepper):
        stepper.level += 1

class Level(object):
    def random_links(self):
        if len(self.linked_rooms) == len(self.rooms):
            return None

        r = random.sample(self.rooms, random.randint(2, 5))

        self.linked_rooms.extend(r)
        self.linked_rooms = list(set(self.linked_rooms))

        return r

    def __init__(self, game):
        self.game = game
        self.downstairs = []
        self.global_room = GlobalRoom(game, self)
        self.rooms = [Room(game, self) for _ in xrange(random.randint(9, 21) + len(game.level_cache) / random.randint(20, 50))]
        self.linked_rooms = []
        self.corridors = [Corridor(game, self, (r[0], r[1])) for r in iter(self.random_links, None)]

        if not self.downstairs:
            c = random.choice([w for y in self.rooms for x in list(y.chunks) for z in x for w in z])
            d = Downstairs(game, c, self)
            c.objects.append(d)
            self.downstairs = [d]

class Game(object):
    def __init__(self):
        self.light_descriptors = [
            "Black",
            "Pretty dark",
            "Dark",
            "Mildly dark",
            "Slightly bright",
            "Bright",
            "White",
        ]

        self.level_cache = []
        self.players = SequentialDict()
        self.starting_chunk = None
        self.generation_chance = {}

        def register_object(co):
            for x in co.__subclasses__():
                self.generation_chance[x] = x.chance

                register_object(x)

        register_object(ChunkObject)

        print "Generating dungeon..."

        self.level_cache.append(Level(self))

        for _ in xrange(random.randint(20, 50) - 2):
            for d in self.level_cache[-1].downstairs:
                self.level_cache.append(Level(self))

                d.target = self.level_cache[-1]

        print "Dungeon generated!"

class Player(object):
    def __init__(self, game, name):
        self.level = 0
        self.chunk = game.starting_chunk
        self.name = name

game = Game()

@plugincon.easy_bot_command("ih_resetgame", True)
def reset_irchack(message, raw):
    if raw:
        return

    global game
    game = Game()

    return "Reset succesfully!"

@plugincon.easy_bot_command("ih_join")
def join_irchack(message, raw):
    if raw:
        return

    global game

    if message["nickname"] in game.players.keys():
        return "You already joined!"

    game.players[message["nickname"]] = Player(game, message["nickname"])

    return [x.format(player=message["nickname"], levels=len(game.level_cache)) for x in [
        "{player}: Welcome to IRCHack!",
        "A game where you are who you want, and let your imagination free",
        "as in reading a book; a game where you make out your OWN story against",
        "the temible monsters of the depths of the Dangling Dungeons of Doom!",
        "...Currently with {levels} flightes of stair down into your quest...",
    ]]

def player_command(command_name):
    def __decorator__(func):
        @plugincon.bot_command(command_name)
        def __wrapper__(message, connector, index, raw):
            if raw:
                return

            global game

            p = message["nickname"]

            if p not in game.players.keys():
                connector.send_message(
                    index,
                    plugincon.get_message_target(connector, message, index),
                    "You didn't join yet!"
                )

            return func(message, connector, index, game.players[message["nickname"]], game)

        return __wrapper__

    return __decorator__

def plot_rooms(num_rooms):
    plt.plot(num_rooms)
    plt.xlabel("Dungeon Floor")
    plt.ylabel("Number of Rooms")

    plt.show()

@plugincon.easy_bot_command("ih_plot", True)
def plot_ih_rooms(message, raw):
    if raw:
        return

    global game

    num_rooms = []

    for l in game.level_cache:
        num_rooms.append(len(l.rooms))

    job = multiprocessing.Process(target=plot_rooms, args=(num_rooms,))
    job.start()

    return "Plotted rooms with success!"
