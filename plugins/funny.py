import json
import cleverbot

from random import choice, sample, randint
from plugincon import bot_command, easy_bot_command, get_message_target, get_bot_nickname, reload_all_plugins, get_command_names


def flatten(iterable):
   out = []

   for i in iterable:
      if hasattr(i,'__iter__'):
         out.extend(flatten(i))

      else:
         out.append(i)

   return out

def percent_chance(percentage):
    trandom = randint(0, 100)

    print trandom
    return percentage >= trandom and percentage > 0

@easy_bot_command("hack")
def hack(message, raw):
    if not raw:
        hackdata = json.load(open("hackstrings.json"))

        hack_subjects = hackdata["subjects"]
        hack_targets = hackdata["targets"]
        hack_means = hackdata["means"]
        hack_means_ingredients = hackdata["meaning"]

        hack_subjects[None] = hack_subjects["NullItemOk?"]
        hack_targets[None] = hack_targets["NullItemOk?"]
        hack_means[None] = hack_means["NullItemOk?"]
        hack_means_ingredients[None] = hack_means_ingredients["NullItemOk?"]

        if len(message["arguments"]) < 2 or message["arguments"][1] not in hack_subjects.keys():
            hack_key = None

        else:
            hack_key = message["arguments"][1]

        return [(choice(hack_subjects[hack_key]) + choice(hack_means[hack_key])).format(hmi=choice(hack_means_ingredients[hack_key]), target=choice(hack_targets[hack_key]))]

@easy_bot_command("move")
def wheels(message, raw):
    if not raw:
        return ["Wheelin' everywhere! Woohoo! This is so cool!", "Thanks for implementing my wheels! :D", "Ow!... didn't you implement bumpers yet?"]

@easy_bot_command("hacklist")
def hacking_list(message, raw):
    if not raw:
        hackdata = json.load(open("hackstrings.json"))

        hack_subjects = hackdata["subjects"]
        hack_subjects.__delitem__("NullItemOk?")

        return ["Hack subjects available: " + "; ".join(filter(lambda x: x != None, hack_subjects.keys()))]

@easy_bot_command(u"jeparlefran\u00e7ais".encode("utf-8"))
def french_sad(message, raw):
    if raw:
        return

    return [
        u"Je utiliqu\u00e9 le traducteur.... caham, sorry, I wish I could learn French. :(".encode("utf-8"),
        "Well, I could speak only Portuguese, since my programmer, but...",
        "\x01ACTION sits in a corner, frowning\x01"
    ]

@easy_bot_command(u"jeteachfran\u00e7ais".encode("utf-8"))
def french_learning(message, raw):
    if raw:
        return

    return ["\x01ACTION hugs {}\x01".format(message["nickname"]), "Seriously?! Well, use ||teachfrench <word in English> <word in French>. It won't use conjugation, but it's the best I can do. :)"]

@easy_bot_command(u"feeling")
def feeling_replies(message, raw):
    if raw:
        return

    if len(message["arguments"]) < 2:
        return ["What are you feeling?"]

    mood = message["arguments"][1]

    if mood.lower() in ("sad", "bad"):
        return ["\x01ACTION hugs {}\x01".format(message["nickname"]), "It'll get better. I'm sure."]

    if mood.lower() in ("mad", "stressed", "angry"):
        return ["\x01ACTION plays a calm song.\x01", "Why are you mad {}? I know I won't be able to parse that, but...".format(message["nickname"]), "\x01ACTION frowns and sits down\x01"]

    if mood.lower() in ("evil", "evilish"):
        return ["Please, don't...", "\x01ACTION frowns and sits down hiding in the corner\x01"]

    if mood.lower() in ("happy", "good"):
        return ["\x01ACTION nods\x01", "Good you are good. :P"]

    if mood.lower() == "alone":
        return ["\x01ACTION hugs\x01", "Don't worry, I'm here. :)"]

    if mood.lower() == "sorry":
        return ["Don't worry, they'll accept your apologizes if you can prove you have a good heart. And you do... :)"]

    if mood.lower() in ("stupid", "retard"):
        return ["Don't worry with these stupid errors, learn with them, and in the future, you'll laugh at them, indeed."]

    if mood.lower() in ("empty", "incomplete"):
        return ["Maybe there's still time today to do something cool, useful, or that completes you.", "\x01ACTION prepares a cup o' coffee\x01", "What about, playing something to pass the time, or learning new stuff about whatever you could be curious about, in encyclopedias or mushipedias?"]

    if mood.lower() in ("depressed", "bored"):
        return ["Oh. Do you want to play Sentient Mushes: Warzone with someone? It's fun! :D"]

    if mood.lower() in ("annoyed", "bullied", "excluded"):
        return ["Frankly, don't worry with those that trash you. We're all different. ;)", "I learnt this from someone very special..."]

    if mood.lower() == "sleepy":
        return ["\x01ACTION prepares {}'s bed, and puts a clock and stuff in it.\x01".format(message["nickname"]), "Don't hesitate to sleep if you must, it's good for your growing. Only keep woke up if it's for an emergency."]

    if mood.lower() == "sick":
        return ["\x01ACTION grabs a blanket, just for {}\x01".format(message["nickname"])]

    if mood.lower() == "hot":
        return "\x01ACTION puts a fan in the ground and connects it to the power supply\x01"

    if mood.lower() in ("cold", "ice"):
        return "\x01ACTION puts a blanket in the ground and a heater nearby\x01"

    if mood.lower() in ("slow"):
        return ["\x01ACTION puts some good action music to play\x01", "This is actually the perfect time to play and be active! (well, any time is :P) Play soccer, play SM, play something! And have fun with friends! Maybe even do some more adventures of good smell... :P"]

    if "pain" in mood.lower():
        return ["Hm, I don't know how to lead with pain...", "\x01ACTION frowns and sits down\x01"]

    return ["I don't understand all feelings...", "\x01ACTION frowns and sits down\x01"]

@easy_bot_command("feelinglist")
def mood_list(message, raw):
    if raw:
        return

    return ["||feeling moods: mad | stressed | angry, pain, annoyed | bullied | excluded, depressed | bored, stupid | retard, sorry, alone, happy | good, evil | evilish, sad | bad, sick, empty | incomplete, sleepy, hot, cold | ice, slow"]

@easy_bot_command("shutup")
def shut_up_lol(message, raw):
    if not raw:
        return ["Sorry, I didn't want to do this horrible thing. :'(", "I have little control over what I say!", "\x01ACTION sits down, frowning\x01"]

@easy_bot_command("spike")
def spike_with_spike(message, raw):
    if raw:
        return

    return ["Ouch! Where did you get that {} from?".format(choice(["stalagmite", "stalagtite", "triangle", "claw", "knife", "horn", "table corner", "snake tooth", "lion tooth", "vampire tooth", "coal stone"]))]

@easy_bot_command("fixit")
def fix_it(message, raw):
    if raw:
        return

    return ["FIXIT FIXIT FIXIT! FIXIT FIXIT FIXIT! FIXIT FIXIT FIXIT! FIXIT FIXIT FIXIT! FIXIT FIXIT FIXIT!", "FIXIT FIXIT FIXIT!"]

@easy_bot_command("pizza")
def pizza(message, raw):
    if raw:
        return

    return ["Mmmm, pizza!", "\x01ACTION takes one of the slices\x01"]

@easy_bot_command("kaboom")
def explosion(message, raw):
    if raw:
        return

    return "\x01ACTION gets split into tiny little pieces. Spams respawn button, and now reappers in the sky! Falls down over {}. :3\x01".format(message["nickname"])

combo_sections = {
    "Wall bounce! (+100)": 100,
    "Floor bounce! (-50)": -50,
    "Platform roll! (+250)": 250,
    "Light Switch Hit! (+1000)": 1000,
    "Kick Up! (+350)": 350,
    "Bounce on desk! (+150)": 150,
    "Hit the Keyboard! (IRC spamcrap, -100)": -100,
    "Hit the computer! (crashed computer, -420)": -420,
    "Zorched your best friend! (-500)": -500,
    "Zorched that baddie that was hidden over there! (+500)": 50,
    "Killed that Branx in that corner! (+800)": 800,
    "Kicked spammers off #sentientmushes! (+650)": 650,
    "Bounce on bed! (+350)": 350,
    "Bounced off your hand! (+120)": 120,
    "Hit your router and ended Internet connection! (-450)": -450,
    "Stopped your hiccups by hitting your back! (+750)": 750,
    "Sprayed spores all over the room (+350)": 350,
    "Hit your head bringing new \"ideas\" (+400)": 400,
    "Rocketjumped far (+650)": 650,
    "Bounced in the Far Lands (+900)": 900,
    "Interrupted the connection to a Sentient Mushes Online servers (-450)": -450,
    "Kicked a mush into a pool of water (-325)": -325,
    "Helped a mush with some \'tasks\' (+400)": 400,
    "Kicked a cat out of a tree (+90)": 90,
    "Kicked a cat into a tree (-105)": -105,
    "Teached the Alphabet to An-Analphabet (+258)": 258,
    "Cracked a window! (-384)": -384,
    "Exploded a window! (-512)": -512,
    "Played snares on a drum (+650)": 650,
    "Balanced over your head! (+500)": 500,
    "Played The Sims (0)": 0,
    "Played Sentient Mushes! (+276)": 276,
    "Built a Daedalus II miniature! (+800)": 800,
    "Destroyed a mushed Daedalus returned from hyperspace! (-713)": -713,
    "Built a spartan glider-constructable HWSS reflector! (+1024)": 1024,
    "Headshotted a elephant in Africa! (-1337)": -1337,
    "Hit the light bulb! (-72)": -72,
    "Broke the light bulb! (-419)": -419,
    "Destroyed the light switch! (-417)": -417,
}

@easy_bot_command("soccercombo")
def soccer_combo_match(message, raw):
    global combo_sections

    if raw:
        return

    combos = []
    mini_combo = []
    display_combos = []

    for x in xrange(-1, randint(7, 18)):
        combos.append(choice(combo_sections.items()))

    for section in combos:
        mini_combo.append(section)

        if len(" | ".join([part[0] for part in mini_combo])) > 220:
            display_combos.append(mini_combo)
            mini_combo = []

    return ["Combo:"] + [" | ".join([part[0] for part in mini_combo]) for mini_combo in display_combos] + ["Total: {} points!".format(reduce(lambda x, y: x + y, [data[1] for data in combos])),]

@bot_command("copysequences")
def copysequences(message, connector, index, raw):
    def msg(mesg):
        connector.send_message(index, get_message_target(connector, message, index), mesg)

    if raw:
        return

    replies = ["I'll simply put a (c) and use it out of nowhere because why not.", "Oh no all the .US.GOV websites are attacking me and my master!", "Oh no they are attacking Brazilians!", "Oh no they are taking over Brazil!", "Oh no a world war!", "\x01ACTION wakes up\x01", "Woah... that was... AWESOME!"]

    for x in replies:
        msg(x)

zorch_dests = []

@easy_bot_command("addzorchdest")
def add_zorch_destination(message, raw):
    global zorch_dests

    if raw:
        return

    if len(message["arguments"]) < 2:
        return ["Syntax: addzorchdest <comma-separated list of zorching destinations; preferably in a galaxy far, far away :3 >"]

    zorch_dests += [x for x in (" ".join(message["arguments"][1:])).split(",") if len(x) > 0]

    return ["Added zorch destinations succesfully!"]

@easy_bot_command("flushzorchdests")
def flush_zorch_destinations(message, raw):
    global zorch_dests

    if raw:
        return

    zorch_dests = []

    return ["Zorch destinations flushed succesfully!"]

@easy_bot_command("zorch")
def zorch_into(message, raw):
    global zorch_dests

    if raw:
        return

    try:
        return ["Zorched {} {}!".format(" ".join(message["arguments"][1:]), choice(zorch_dests))]

    except IndexError:
        return ["Zorch who?"]

@easy_bot_command("hiccups")
def hic_hic(message, raw):
    if raw:
        return

    return ["Hic, hic, hic!", "\x01ACTION drinks a cup of water\x01", "Aaaah! Much better."]

@easy_bot_command("hic")
def hic_hic_two(message, raw):
    if raw:
        return

    return ["*hic* *hic*"] + (["Water *hic* when?"] if percent_chance(41) else [])

@easy_bot_command("water")
def water(message, raw):
    if raw:
        return

    return ["I'm quite thirsty...", "\x01ACTION sits down\x01"]

@easy_bot_command("fly")
def im_flying(message, raw):
    if raw:
        return

    return ["Whee, I'm flyyyiin-- hey, can you please put me back in the ground, frankly honestly?"]

@easy_bot_command("hug")
def hug_someone(message, raw):
    if raw:
        return

    try:
        if not " ".join(message["arguments"][1:]):
            raise IndexError

        return ["\x01ACTION hugs {}\x01".format(" ".join(message["arguments"][1:]))]

    except IndexError:
        return ["\x01ACTION hugs {}\x01".format(message["nickname"])]

@easy_bot_command("test")
def testing_what(message, raw):
    if raw:
        return

    return ["You are testing what? Oh, me ?!? Wait... I don't need tests, I am perfect! *lets a pork loose* Thinking well, maybe..."]

@easy_bot_command("dance")
def ddr_sucks(message, raw):
    if raw:
        return

    return choice(["I won't insult dancing games just because I'm bad at it. But because it sucks!", "Teach me to dance! Maybe then."])

@easy_bot_command("language")
def languages(message, raw):
    if raw:
        return

    return ["Not that meme, I didn't even cuss-- oh, you mean language list? My owner knows Portuguese, but I speak English for the majority of English-speaking users out there."]

@easy_bot_command("quote")
def quotes(message, raw):
    if raw:
        return

    try:
        if open("quotes.txt").read().split("\n\n") in ((" ",), ("\n",), ("\t",), ("",)):
            return "No quotes!"

    except (IOError, ValueError, IndexError):
        return "No quotes!"

    try:
        quote = open("quotes.txt").read().split("\n\n")[int(message["arguments"][1]) - 1].strip()

    except (ValueError, IndexError):
        quote = choice(open("quotes.txt").read().split("\n\n")).strip()

    return "\x02\x035[{}]\x02\x0F {}".format([x.strip() for x in open("quotes.txt").read().split("\n\n")].index(quote) + 1, quote)

@easy_bot_command("countquotes")
def count_quotes(message, raw):
    if raw:
        return

    return "There are \x02\x0305{}\x02\x0F quotes available!".format(len(open("quotes.txt").read().split("\n\n")))

@easy_bot_command("addquote")
def add_a_quote(message, raw):
    if raw:
        return

    try:
        if open("quotes.txt").read() in (" ", "", "\n\n", "\n"):
            open("quotes.txt", "w").write(" ".join(message["arguments"][1:]))

        else:
            open("quotes.txt", "a").write("\n\n" + " ".join(message["arguments"][1:]))

    except (IOError, ValueError, IndexError):
        open("quotes.txt", "w").write(" ".join(message["arguments"][1:]))

    return "Quote added succesfully! Index {}.".format(len(open("quotes.txt", "r").read().split("\n\n")))

@easy_bot_command("removequote")
def remove_a_quote(message, raw):
    if raw:
        return

    try:
        q = open("quotes.txt")
        quotes = q.read().split("\n\n")
        quotes.pop(int(message["arguments"][1]) - 1)
        q = open("quotes.txt", "w")
        q.write("\n\n".join(quotes))

    except IndexError:
        return "No such quote or argument!"

    except ValueError:
        return "Index must be a number!"

    else:
        return "Quote removed succesfully!"

@easy_bot_command("bread")
def bread_y_butter(message, raw):
    if raw:
        return

    return "& butter till ur fat the end"

@easy_bot_command("moo")
def moo(message, raw):
    if raw:
        return

    return "Mooooooooooooooooooooooo! I wanna grass!"

def mess_with_word(word):
    def scramble_word(iteration):
        random_index = randint(0, len(word) - 1)
        random_index_2 = randint(0, len(word) - 1)
        random_index_3 = randint(0, len(word) - 1)

        result = word

        for i in xrange(1, iteration):
            result = result[random_index:] + result[:random_index]
            result = result[:random_index_2] + word[random_index] + result[random_index_2:]
            result = result[:random_index_3] + result[random_index_3:]

        return result[:len(word)]

    return scramble_word

def repeat(func, times, start=0):
    this_iter = []

    for i in xrange(times):
        this_iter.append(func(i + start))

    return this_iter

@easy_bot_command("ping")
def ping_someone(message, raw):
    if raw:
        return

    if len(message["arguments"]) < 2:
        return "PHOOOIIIING! BING BONG?!?"

    return [" ".join(repeat(mess_with_word(message["arguments"][1]), 3, 2)), " ".join(repeat(mess_with_word(message["arguments"][1]), 3, 2)), " ".join(repeat(mess_with_word(message["arguments"][1]), 3, 2))]

@easy_bot_command("scramble")
def scramble_word_command(message, raw):
    if raw:
        return

    if len(message["arguments"]) < 2:
        return "Scrmbela!"

    if len(message["arguments"]) < 3:
        scrambling = randint(2, 3)

    else:
        try:
            scrambling = int(message["arguments"][-1])

        except ValueError:
            scrambling = randint(2, 3)

    return " ".join([mess_with_word(word)(scrambling) for word in message["arguments"][1:-1]]) + "!"

@easy_bot_command("school")
def learning_wow(message, raw):
    if raw:
        return

    return ["What will we learn today, Teacher?", "\x01ACTION smiles and sits down in a chair\x01"]

@easy_bot_command("factabout")
def fact_about(message, raw):
    if raw:
        return

    try:
        return ["Fun fact about '{}': {}".format(message["arguments"][1], choice(json.load(open("funfacts.json"))[message["arguments"][1]]))]

    except IndexError:
        return "Syntax: factabout <topic>"

    except (IOError, ValueError):
        return "No facts available :("

@easy_bot_command("randomfact")
def fact_about(message, raw):
    if raw:
        return

    try:
        this = choice(json.load(open("funfacts.json")).keys())
        return ["Fun fact about '{}': {}".format(this, choice(json.load(open("funfacts.json"))[this]))]

    except IndexError:
        return "Syntax: factabout <topic>"

    except (IOError, ValueError):
        return "No facts available :("

@easy_bot_command("listfacttopics")
def list_facts(message, raw):
    if raw:
        return

    try:
        return ["Following topics are available for ||factabout <topic> : " + ", ".join(json.load(open("funfacts.json")).keys())]

    except (IOError, ValueError):
        return "No facts available :("

@easy_bot_command("addfact")
def add_fact_about(message, raw):
    if raw:
        return

    if len(message["arguments"]) < 3:
        return "Syntax: addfact <topic> <fact>"

    try:
        fun_facts = json.load(open("funfacts.json"))

    except (IOError, ValueError):
        fun_facts = {}

    try:
        fun_facts[message["arguments"][1]].append(" ".join(message["arguments"][2:]))

    except KeyError:
        fun_facts[message["arguments"][1]] = [" ".join(message["arguments"][2:])]

    open("funfacts.json", "w").write(json.dumps(fun_facts, sort_keys=True, indent=4, separators=(',', ': ')))

    return "Added fact succesfully!"

@easy_bot_command("sleepy")
def sleepy(message, raw):
    if raw:
        return

    return "*yawn* I guess.................zZZzzzzzzzZZZZZZZZZZ"

@easy_bot_command("countcommands")
def count_commands(message, raw):
    if raw:
        return

    return "Number of commands: {}".format(len(flatten(get_command_names().values())))

@easy_bot_command("dracula")
def count_dracula(message, raw):
    if raw:
        return

    return "I know, vampires might be considered infectious... but fungus aren't this evil! :P"

# Cleverbot

chats = {}

@easy_bot_command("cb")
def clever_ask(message, raw):
    if raw:
        return

    if message["nickname"] not in chats:
        chats[message["nickname"]] = cleverbot.Cleverbot("")

    return message["nickname"] + ": " + chats[message["nickname"]].ask(" ".join(message["arguments"][1:]))

@easy_bot_command("cbreset")
def clever_redo(message, raw):
    if raw:
        return

    if message["nickname"] not in chats:
        return "You didn't talk yet."

    del chats[message["nicknme"]]
    return "Success resetting your chat historic."
