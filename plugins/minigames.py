from random import randint
from time import sleep
from plugincon import bot_command, easy_bot_command, get_message_target, get_bot_nickname, reload_all_plugins

def percent_chance(percentage):
	trandom = randint(0, 100)

	print trandom, percentage
	return percentage >= trandom and percentage > 0

# Sentient Mushes: IRC Warzone

user_data = {}

ammo_data = {
	"rockets": {
		"weapons": [
			"rockox",
		],
		"cost": 10,
		"amount": 1,
	},
	"serum": {
		"weapons": [
			"serum",
		],
		"cost": 2,
		"amount": 2,
	},
	"gas": {
		"weapons": [
			"gas",
		],
		"cost": 2,
		"amount": 1,
	},
	"clips": {
		"weapons": [
			"machinegun",
		],
		"cost": 5,
		"amount": 2,
	},
}

weapon_data = {
	"gas": {
		"damage": 3,
		"damagefungus": 14,
		"drainfungushealth": True,
		"drainhealth": True,
		"randomrange": 4,
		"cost": 20,
		"ammotype": "gas",
	},
	"serum": {
		"damagefungus": 8,
		"damage": 0,
		"drainfungushealth": True,
		"drainhealth": False,
		"randomrange": 10,
		"cost": 5,
		"ammotype": "serum",
	},
	"rockox": {
		"damagefungus": 22,
		"damage": 72,
		"drainfungushealth": False,
		"drainhealth": True,
		"randomrange": 40,
		"cost": 50,
		"ammotype": "rockets",
	},
	"machinegun": {
		"damagefungus": 4,
		"damage": 34,
		"drainhealth": True,
		"drainfungushealth": False,
		"randomrange": 10,
		"cost": 18,
		"ammotype": "clips",
	},
}

@easy_bot_command("smw_findspore")
def smw_search_for_spores(message, raw):
	if raw:
		return
		
	user = message["nickname"]
	
	if user not in user_data.keys():
		return ["Join the game first using ||smw_join !"]
		
	if not percent_chance(32):
		return ["No spore found!"]
		
	if user_data[user]["mush"]:
		return ["Found a random spore! Absorbing... Now you have {} spores!".format(user_data[user]["spores"])]
		
	if percent_chance(72):
		return ["Found a spore... but wait, was that meant to happen? Now you are... a mush!"]
		
	else:
		return ["You found a spore! But wait... why were you looking for spores?", "Do you want to plant champignons or didn't you know the danger of this?"]

@easy_bot_command("smw_join")
def join_warzone_stats(message, raw):
	if raw:
		return

	user = message["nickname"]
	is_mush = percent_chance(48)
	
	if user in user_data.keys():
		return ["You already joined the game! To quit (suicide), use ||smw_quit ."]
		
	user_data[user] = {
		"host": message["host"],
		"money": 30,
		"mush": is_mush,
		"spores": (0 if not is_mush else 6),
		"immune": (5 if not is_mush else 0),
		"ammo": {
			"gas": (4 if not is_mush else 0),
			"serum": (6 if not is_mush else 0),
			"rockets": 2,
			"clips": 5,
		},
		"weapons": {
			"gas": False,
			"serum": (True if not is_mush else False),
			"rockox": False,
			"machinegun": False,
		},
		"health": 100,
		"fungushealth": (100 if is_mush else 0),
		"armor": 0,
	}
	
	return ["You were added to the game! You are{}a mush!".format((" not " if not is_mush else " "))]

@easy_bot_command("smw_players")
def smw_player_list(message, raw):
	if raw:
		return
		
	player_list = []
	mini_player_list = []
	
	for player in user_data.keys():
		mini_player_list.append(player.encode('utf-8'))
		
		if len(mini_player_list) % 30 == 0:
			player_list.append(mini_player_list)
			mini_player_list = []
			
	if len(player_list) < 1 or player_list[-1][-1] != mini_player_list[-1]:
		player_list.append(", ".join(mini_player_list))
	return ["Players: "] + player_list
	
@easy_bot_command("smw_shoot")
def smw_shoot_at(message, raw):
	if raw:
		return
	
	if len(message["arguments"]) < 3:
		return ["Syntax: smw_shoot <target> <weapon>"]
	
	user = message["nickname"]
	target = message["arguments"][1]
	weapon = message["arguments"][2]
	
	if message["nickname"] not in user_data.keys():
		return ["Join the game first using ||smw_join !"]
	
	if target not in user_data.keys():
		return ["Who is that? I don't think he's aboard either."]
	
	if weapon not in weapon_data.keys():
		return ["Uh, did you invent that shiny new weapon?"]
		
	if not user_data[message["nickname"]]["weapons"][weapon]:
		return ["You don't have that weapon, sorry!"]
		
	gun = weapon_data[weapon]
	
	realdamage = gun["damage"] + randint(-gun["randomrange"], gun["randomrange"])
	realfdamage = gun["damagefungus"] + randint(-gun["randomrange"], gun["randomrange"])
	
	if user_data[user]["ammo"][weapon_data[gun]["ammotype"]] < 1:
		return ["You are loading empty clips!"]
	
	if realdamage < 0:
		realdamage = 0
		
	if realfdamage < 0:
		realfdamage = 0
	
	if gun["drainhealth"]:
		user_data[target]["health"] -= realdamage
		
	if gun["drainfungushealth"] and user_data[target]["mush"]:
		user_data[target]["fungushealth"] -= realfdamage
		
	if user_data[target]["fungushealth"] < 1:
		user_data[user]["money"] += 50
		user_data[target]["mush"] = False
		return ["{} is not a mush anymore!".format(target)]
	
	if user_data[target]["health"] < 1:
		user_data[user]["money"] += 30
		user_data.__delitem__(target)
		return ["{} is now dead! He's out of the game! Rejoin?".format(target)]
		
	if user_data[target]["mush"] != user_data[user]["mush"]:
		user_data[user]["money"] += 5
		
	if not user_data[target]["mush"]:
		return ["Dealt {} damage into the target!".format((real_damage if gun["drainhealth"] else 0))]
		
	else:
		return ["Dealt {} damage into the target plus {} damage to the fungus!".format((real_damage if gun["drainhealth"] else 0), (realfdamage if gun["drainfungushealth"] else 0))]
		
@easy_bot_command("smw_extract")
def smw_extract_spore(message, raw):
	if raw:
		return
	
	user = message["nickname"]
		
	if user not in user_data.keys():
		return ["Join the game first using ||smw_join !"]
		
	if not user_data[user]["mush"]:
		return ["You are not one of these yet! Hey, do you want to be one?..."]
		
	if user_data[user]["spores"] >= 15:
		return ["Max spores reached! (15)"]
		
	user_data[user]["spores"] += 1
	return ["Extracted a spore! (now with {})".format(user_data[user]["spores"])]
	
@easy_bot_command("smw_spike")
def spike_user_with_spore(message, raw):
	if raw:
		return
		
	user = message["nickname"]
	
	if user not in user_data.keys():
		return ["Join the game first using ||smw_join !"]
		
	target = message["arguments"][1]
	
	if target not in user_data.keys():
		return ["Who is your target? Is it even aboard?"]
		
	if not user_data[user]["mush"]:
		return ["Where do you think you'll get spores from?"]
		
	if user_data[target]["mush"]:
		return ["He's already one!"]
		
	if user_data[user]["spores"] < 1:
		return ["Sorry, out of spores."]
		
	user_data[user]["spores"] -= 1
	user_data[target]["immune"] -= 1
	
	if user_data[target]["immune"] < 1:
		user_data[target]["fungushealth"] = 80
		user_data[target]["mush"] = True
		return ["Infection succesful! Now {} is a mush!".format(target)]
	
	return ["Spiking succesful! But, he will take more than that; his immune system is now already {} though!".format(user_data[target]["immune"])]
	
@easy_bot_command("smw_quit")
def smw_quit(message, raw):
	if raw:
		return
		
	user = message["nickname"]
	
	if not user in user_data.keys():
		return ["You are not joined either!"]
		
	user_data.__delitem__(user)
	
	return ["Suicide succesful! :3"]
	
@easy_bot_command("smw_status")
def smw_user_status(message, raw):
	if raw:
		return
		
	user = message["nickname"]
	
	if user not in user_data.keys():
		return ["Join the game first using ||smw_join !"]
	
	return [
		"{} Status:".format(user),
		"You have {} money.".format(user_data[user]["money"]),
		"You are{}a mush.".format((" not " if not user_data[user]["mush"] else " ")),
		"You have {} health{}.".format(user_data[user]["health"], (" ({} fungus health)".format(user_data[user]["fungushealth"]) if user_data[user]["mush"] else "")),
		"You have immune system of {} in the Rehermann scale.".format(user_data[user]["immune"]),
		"You have the following weapons: " + ", ".join([weapon for weapon, data in user_data[user]["weapons"].items() if data]),
		"You have the following ammunition: " + ", ".join(": ".join([ammo[0], str(ammo[1])]) for ammo in user_data[user]["ammo"].items()),
	] + ([] if not user_data[user]["mush"] else [
		"You have {} spores.".format(user_data[user]["spores"])
	])
	
@easy_bot_command("smw_getstatus")
def smw_get_user_status(message, raw):
	if raw:
		return
		
	user = message["nickname"]
		
	try:
		target = message["arguments"][1]
		
	except IndexError:
		return ["Syntax: smw_getstatus <user>"]
		
	if target not in user_data.keys():
		return ["Error: Target didn't join!"]
	
	return [
		"{} Status:".format(target),
		"He/she has {} money.".format(user_data[target]["money"]),
		"He/she is{}a mush.".format((" not " if not user_data[target]["mush"] else " ")),
		"He/she has {} health{}.".format(user_data[target]["health"], (" ({} fungus health)".format(user_data[target]["fungushealth"]) if user_data[target]["mush"] else "")),
		"He/she has immune system of {} in the Rehermann scale.".format(user_data[target]["immune"]),
		"He/she has the following weapons: " + ", ".join([weapon for weapon, data in user_data[target]["weapons"].items() if data]),
		"He/she has the following ammunition: " + ", ".join(": ".join([ammo[0], str(ammo[1])]) for ammo in user_data[target]["ammo"].items()),
	] + ([] if not user_data[target]["mush"] else [
		"He/she has {} spores.".format(user_data[target]["spores"])
	])
	
@easy_bot_command("smw_about")
def smw_about(message, raw):
	if raw:
		return
		
	return [
		"Sentient Mushes(TM): Warzone CC-BY-NC 2016 Gustavo Ramos \"Gustavo6046\" Rehermann.",
		"Source code is CC-BY-NC. For more info please visit https://creativecommons.org/licenses/by-nc/2.0/ .",
		"Source code at: https://www.github.com/Gustavo6046/GusBot-2",
		" ",
		"Sentient Mushes series; Inspired by another Twinoidian game."
	]
	
@easy_bot_command("smw_buygun")
def smw_buy_a_big_weapon(message, raw):
	if raw:
		return
		
	user = message["nickname"]
	
	if not user in user_data.keys():
		return ["Join the game first using ||smw_join !"]
		
	try:
		weapon = message["arguments"][1]
		
	except IndexError:
		return ["Syntax: smw_buygun <gun's name>"]
		
	money = user_data[user]["money"]
	
	if weapon not in weapon_data.keys():
		return ["You can't buy your inventions; they're already yours!", "Well, maybe of your imagination, that is... :3"]
		
	if user_data[user]["weapons"][weapon]:
		return ["You already have that weapon!"]
		
	if user_data[user]["money"] < weapon_data[weapon]["cost"]:
		return ["Too little money!"]
		
	user_data[user]["money"] -= weapon_data[weapon]["cost"]
	user_data[user]["weapons"][weapon] = True
	return "Bought weapon succesfully!"
	
@easy_bot_command("smw_buyammo")
def smw_buy_a_big_weapon(message, raw):
	if raw:
		return
		
	user = message["nickname"]
	
	if not user in user_data.keys():
		return ["Join the game first using ||smw_join !"]
		
	try:
		ammo_type = message["arguments"][1]
		
	except IndexError:
		return ["Syntax: smw_buyammo <ammo type>"]
		
	money = user_data[user]["money"]
	
	if ammo_type not in ammo_data.keys():
		return ["You can't buy your inventions; they're already yours!", "Well, maybe of your imagination, that is... :3"]
		
	if user_data[user]["money"] < ammo_data[ammo_type]["cost"]:
		return ["Too little money!"]
		
	user_data[user]["money"] -= ammo_data[ammo_type]["cost"]
	user_data[user]["ammo_data"][ammo_type] += ammo_data[ammo_type]["buyamount"]
	return "Bought weapon succesfully!"
	
@easy_bot_command("smw_listweaponry")
def list_weaponry(message, raw):
	if raw:
		return

	return ["Weapons: " + ", ".join(weapon_data.keys())]
	
@easy_bot_command("smw_listammotypes")
def list_ammos(message, raw):
	if raw:
		return
		
	return ["Ammo types: " + ", ".join(ammo_data.keys())]
	
@bot_command("GETNICKCHANGES0")
def get_nick_changes(message, connector, index, raw):
	if not raw:
		return
		
	try:
		if message.split(" ")[1].upper() != "NICK":
			return
			
	except IndexError:
		return
	
	old_nick = message.split("!")[0]
	
	try:
		new_nick = message.split(" ")[2]
		
	except IndexError:
		return
		
	user_data[new_nick] = user_data[old_nick]
	user_data.__delitem__(old_nick)
	
@easy_bot_command("smw_resetmatch", True)
def reset_smw_match(message, raw):
	global user_data

	if raw:
		return
		
	user_data = {}
		
	return ["Reset with success!", "...Anyone gonna join now?"]