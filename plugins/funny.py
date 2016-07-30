import json

from random import choice, sample, randint
from plugincon import bot_command, easy_bot_command, get_message_target, get_bot_nickname, reload_all_plugins


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
		u"Le utiliqu\u00e9 le traducteur.... caham, sorry, I wish I could learn French. :(".encode("utf-8"),
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
	
	if mood.lower() in ("mad", "stressed", "tired", "angry"):
		return ["\x01ACTION plays a calm song.\x01", "Why are you mad {}? I know I won't be able to parse that, but...".format(message["nickname"]), "\x01ACTION frowns and sits down\x01"]
		
	if mood.lower() in ("evil", "evilish"):
		return ["Please, don't...", "\x01ACTION frowns and sits down hiding in the corner\x01"]
		
	if mood.lower() in ("happy", "good"):
		return ["\x01ACTION nods\x01", "Good you are good. :P"]
	
	if "pain" in mood.lower():
		return ["Hm, I don't know how to lead with pain...", "\x01ACTION frowns and sits down\x01"]
		
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
}

@easy_bot_command("soccercombo")
def soccer_combo_match(message, raw):
	global combo_sections

	if raw:
		return
		
	combos = []
	
	for x in xrange(-1, randint(4, 9)):
		combos.append(choice(combo_sections.items()))
		
	return "Combo: {} -> {} points!".format(" | ".join([data[0] for data in combos]), reduce(lambda x, y: x + y, [data[1] for data in combos]))
	
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
		
	print [x for x in " ".join(message["arguments"][1:]).split(",") if len(x) > 0]
		
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
		