import time

from threading import Thread
from random import sample, randint, choice, random
from plugincon import bot_command, easy_bot_command, get_message_target, get_bot_nickname


channel_data = {}

def percent_chance(percentage):
	trandom = randint(0, 100)

	print trandom
	return percentage >= trandom and percentage > 0

def timebomb_explode(index, message, user, connector):
	def msg(msg):
		connector.send_message(index, get_message_target(connector, message, index), msg)
		
	msg("BOOOOOOM!!!!!! There goes {}!".format(user))
	channel_data[message["channel"]]["timebomb_running"] = False
	connector.send_command(index, "KICK {} {} :Exploded into pieces!".format(message["channel"], user))

def wait_for_timebomb(time, index, message, user, connector):
	print "Called!"
	time.sleep(time)
	print "Time gone!"
	
	if channel_data[message["channel"]]["timebomb_running"]:
		timebomb_explode(index, message, user, connector)
		
@bot_command("timebomb_cutwire")
def cut_wire_for_timebomb(message, connector, index, raw):
	def msg(mesg):
		connector.send_message(index, get_message_target(connector, message, index), mesg)
		
	def hlmsg(mesg):
		msg("{}: {}".format(message["nickname"], mesg))

	if raw:
		return
		
	if not message["channel"].startswith("#"):
		msg("Run this command on a channel!")
		return
		
	if not message["channel"] in channel_data.keys() or not channel_data[message["channel"]]["timebomb_running"]:
		hlmsg("This channel doesn't have any timebomb running yet!")
		return
		
	if channel_data[message["channel"]]["target"] != message["nickname"]:
		hlmsg("Don't worry, you are not being targeted for this timebomb! :)")
		return
		
	if message["arguments"] < 2:
		hlmsg("Insert the color of the wire as an argument!")
		return
		
	if message["arguments"][1] == channel_data[message["channel"]]["current_wire"]:
		channel_data[message["channel"]]["timebomb_running"] = False
		hlmsg("Congratulations! You have cut the timebomb!")
		return
		
	hlmsg("Wrong wire! :P")
	Thread(target=timebomb_explode, args=(index, message, message["nickname"], connector)).start()
	
@bot_command("shoot")
def shoot_at(message, connector, index, raw):
	if raw:
		return
		
	def msg(msg):
		connector.send_message(index, get_message_target(connector, message, index), msg)
		
	def hlmsg(msg):
		msg("{}: {}".format(message["nickname"], msg))
		
	if not message["channel"].startswith("#"):
		msg("Run this command on a channel!")
		return
		
	if len(message["arguments"]) < 2:
		hlmsg("Argument syntax: shoot <target>")
		return
		
	for target in message["arguments"][1:]:
		if target == get_bot_nickname(connector, index):
			hlmsg("Nobody can kill me!")
			connector.send_command(index, "KICK {} {} :Trying to kill ME?!?".format(message["channel"], message["nickname"]))
			continue
	
		msg("{} tries to shoot at {}! SHOTS FIRED!!".format(message["nickname"], target))
		
		if percent_chance(15):
			msg("{} accidentally shoots at himself!".format(message["nickname"]))
			connector.send_command(index, "KICK {} {} :Shot down!".format(message["channel"], message["nickname"]))
			continue
			
		if percent_chance(30):
			msg("{} shot {} down!".format(message["nickname"], target))
			connector.send_command(index, "KICK {} {} :Shot down!".format(message["channel"], target))
			continue
			
		msg("He missed the shot!")
		
@bot_command("timebomb")
def timebomb_user(message, connector, index, raw):
	global wire_colors
	global current_wire
	global wire_colors_chooseable
	
	wire_colors_chooseable = map(lambda x: x.strip("\n"), open("randomcolors.txt").readlines())
	
	if raw:
		return

	def msg(mesg):
		connector.send_message(index, get_message_target(connector, message, index), mesg)
		
	def hlmsg(mesg):
		msg("{}: {}".format(message["nickname"], mesg))
		
	def hlmsg2(user, mesg):
		msg("{}: {}".format(user, mesg))
		
	if not message["channel"].startswith("#"):
		msg("Run this command on a channel!")
	
	if not message["channel"] in channel_data.keys():
		channel_data[message["channel"]] = {}
		
	if "timebomb_running" in channel_data[message["channel"]].keys() and channel_data[message["channel"]]["timebomb_running"]:
		msg("The timebomb is already running!")
		return

	if len(message["arguments"]) < 2:
		hlmsg("Argument syntax: timebomb <user> [counter = 30 seconds] [no. of wire colors = random between 4 and 20]")
		return
	
	channel_data[message["channel"]]["target"] = message["arguments"][1]
	
	channel_data[message["channel"]]["timebomb_running"] = True
	
	if len(message["arguments"]) < 3:
		hlmsg("Using 30 seconds for time fuse!")
		time_fuse = 30
		
	else:
		time_fuse = int(message["arguments"][2])
		
	print sample(wire_colors_chooseable, randint(4, 20))
		
	channel_data[message["channel"]]["wire_colors"] = sample(wire_colors_chooseable, randint(4, 20))
		
	if len(message["arguments"]) < 4:
		channel_data[message["channel"]]["current_wire"] = choice(channel_data[message["channel"]]["wire_colors"])
		hlmsg("Using {} wire colors: {}".format(len(channel_data[message["channel"]]["wire_colors"]), ", ".join(channel_data[message["channel"]]["wire_colors"])))
		
	else:
		if int(message["arguments"][3]) > len(wire_colors_chooseable):
			hlmsg("Not so many colors can be chosen!")
			channel_data[message["channel"]]["timebomb_running"] = False
			return
	
		channel_data[message["channel"]]["wire_colors"] = sample(wire_colors_chooseable, int(message["arguments"][3]))
		channel_data[message["channel"]]["current_wire"] = choice(channel_data[message["channel"]]["wire_colors"])
		hlmsg("Using {} wire colors: {}".format(len(channel_data[message["channel"]]["wire_colors"]), ", ".join(channel_data[message["channel"]]["wire_colors"])))
		
	print "Correct wire: " + channel_data[message["channel"]]["current_wire"]
		
	hlmsg2(message["arguments"][1], "A timebomb was implanted on your chest! To escape it, cut the right wire between the following {} colors: {}. Use ||timebomb_cutwire! Be quick, since you only have {} seconds!".format(len(channel_data[message["channel"]]["wire_colors"]), ", ".join(channel_data[message["channel"]]["wire_colors"]), time_fuse))

	Thread(target=wait_for_timebomb, args=(time_fuse, index, message, message["nickname"], connector)).start()