import os

from random import randint, choice, random
from time import sleep
from json import dumps, load
from plugincon import bot_command, easy_bot_command, get_message_target, get_bot_nickname, reload_all_plugins, at_plugin_load, at_plugin_reload


def percent_chance(percentage):
	trandom = randint(0, 100)

	print trandom, percentage
	return percentage >= trandom and percentage > 0

# Sentient Mushes: IRC Warzone

num_bots = 0
capsname = {}
user_data = {}
turns = []
turn_index = 0
condense_bot_messages = False

ammo_data = {
	"rockets": {
		"weapons": [
			"rockox",
		],
		"cost": 10,
		"amount": 1,
		"defaultvalue": 2,
	},
	"serum": {
		"weapons": [
			"serum",
			"retroserum",
		],
		"cost": 2,
		"amount": 2,
		"defaultvalue": 5,
	},
	"heal": {
		"weapons": [
			"healgun"
		],
		"cost": 1,
		"amount": 2,
		"defaultvalue": 4,
	},
	"gas": {
		"weapons": [
			"gas",
		],
		"cost": 2,
		"amount": 1,
		"defaultvalue": 3,
	},
	"clips": {
		"weapons": [
			"machinegun",
			"pistol",
		],
		"cost": 5,
		"amount": 2,
		"defaultvalue": 4,
	},
	"aids": {
		"weapons": [
			"aidsgun",
		],
		"cost": 2,
		"amount": 3,
		"defaultvalue": 2,
	}
}

weapon_data = {
	"gas": {
		"damage": 3,
		"damagefungus": 14,
		"damageimmune": 0,
		"drainimmunehealth": False,
		"drainfungushealth": True,
		"drainhealth": True,
		"randomrange": 4,
		"randomimmunerange": 0,
		"cost": 20,
		"ammotype": "gas",
		"flags": [
		],
	},
	"healgun": {
		"damage": -36,
		"damagefungus": -20,
		"damageimmune": -0.3,
		"drainimmunehealth": False,
		"drainfungushealth": True,
		"drainhealth": True,
		"randomrange": 13,
		"randomimmunerange": 0.3,
		"cost": 4,
		"ammotype": "heal",
		"flags": [
			"nocheckneghealth",
		],
	},
	"pistol": {
		"damagefungus": 1,
		"damage": 19,
		"damageimmune": 0,
		"drainimmunehealth": False,
		"drainhealth": True,
		"drainfungushealth": False,
		"randomrange": 25,
		"randomimmunerange": 0,
		"cost": 6,
		"ammotype": "clips",
		"flags": [
		],
	},
	"serum": {
		"damagefungus": 8,
		"damage": 0,
		"damageimmune": 0,
		"drainimmunehealth": False,
		"drainfungushealth": True,
		"drainhealth": False,
		"randomrange": 10,
		"randomimmunerange": 0,
		"cost": 5,
		"ammotype": "serum",
		"flags": [
		],
	},
	"serum": {
		"damagefungus": 19,
		"damage": 0,
		"damageimmune": 0,
		"drainimmunehealth": False,
		"drainfungushealth": True,
		"drainhealth": False,
		"randomrange": 25,
		"randomimmunerange": 0,
		"cost": 5,
		"ammotype": "serum",
		"flags": [
		],
	},
	"rockox": {
		"damagefungus": 0,
		"damage": 72,
		"damageimmune": 0,
		"drainimmunehealth": False,
		"drainfungushealth": False,
		"drainhealth": True,
		"randomrange": 40,
		"randomimmunerange": 0,
		"cost": 50,
		"ammotype": "rockets",
		"flags": [
		],
	},
	"machinegun": {
		"damagefungus": 4,
		"damage": 34,
		"damageimmune": 0,
		"drainimmunehealth": False,
		"drainhealth": True,
		"drainfungushealth": False,
		"randomimmunerange": 0,
		"randomrange": 10,
		"cost": 18,
		"ammotype": "clips",
		"flags": [
		],
	},
	"aidsgun": {
		"damagefungus": 0,
		"damage": 1,
		"damageimmune": 1.482,
		"drainimmunehealth": True,
		"drainhealth": True,
		"drainfungushealth": False,
		"randomrange": 6,
		"randomimmunerange": 1.6,
		"cost": 11.5,
		"ammotype": "aids",
		"flags": [
		],
	}
}

shoot_succesfull = True

def randf(a, b):
	if a <= 0:
		return random() * b
		
	return (random() + a) * b / a

def shoot(user, target, weapon, bot=False):
	global turn_index
	global turns
		
	gun = weapon_data[weapon]
	
	realdamage = gun["damage"] + randf(-gun["randomrange"], gun["randomrange"])
	realfdamage = gun["damagefungus"] + randf(-gun["randomrange"], gun["randomrange"])
	realidamage = gun["damageimmune"] + randf(-gun["randomimmunerange"], gun["randomimmunerange"])
	
	if user_data[user.lower()]["ammo"][weapon_data[weapon]["ammotype"]] < 1:
		shoot_succesfull = False
		if not bot:
			return ["You are loading empty clips!"]
			
		return ["{} is loading empty clips!".format(capsname[user.lower()])]
		
	try:
		if turns[turn_index] != user.lower():
			print turns[turn_index]
			print user.lower()
			
			shoot_succesfull = False
			return ["Hey! It's not your turn! Stop breaking the queue!"]
			
	except IndexError:
		shoot_succesfull = False
		return ["Nobody's playing! There's no turn to pass!"]
		
	turn_index += 1
	
	if turn_index >= len(turns):
		turn_index = 0
	
	user_data[user.lower()]["ammo"][gun["ammotype"]] -= 1

	if "nocheckneghealth" not in [x.lower() for x in gun["flags"]]:
		if realdamage < 0:
			realdamage = 0
			
		if realfdamage < 0:
			realfdamage = 0
			
		if realidamage < 0:
			realidamage = 0
	
	if gun["drainhealth"]:
		user_data[target.lower()]["health"] -= realdamage
		
	if gun["drainfungushealth"] and user_data[target.lower()]["mush"]:
		user_data[target.lower()]["fungushealth"] -= realfdamage
		
	if gun["drainimmunehealth"]:
		user_data[target.lower()]["immune"] -= realidamage
		
		if user_data[target.lower()]["immune"] <= 0:
			if user_data[target.lower()]["mush"]:
				user_data[target.lower()]["immune"] = 0
				
			else:
				user_data.__delitem__(target.lower())
		
				for i, x in enumerate(turns):
					if x == target.lower():
						turns.pop(i)
				
				if turn_index >= len(turns):
					turn_index = 0
				
				user_data[user.lower()]["stats"]["AIDS Overdoses"] += 1
				user_data[user.lower()]["stats"]["Kills"] += 1
				
				if not bot:
					return ["{} received an AIDS overdose! He's out of the game! Rejoin?".format(target)]
					
				return ["{} overdosed {} with AIDS using {}! He's out of the game!".format(capsname[user.lower()], capsname[target.lower()], weapon)]
				
		if not bot:
			return ["{} received a {} damage on immune!".format(capsname[target.lower()], realidamage)]
			
		return ["{} shot {} with {} to receive {} damage on immune!".format(capsname[user.lower()], weapon, capsname[target.lower()], realidamage)]
		
	if user_data[target.lower()]["health"] <= 0:
		user_data.__delitem__(target.lower())
		
		for i, x in enumerate(turns):
			if x == target.lower():
				turns.pop(i)
		
		if turn_index >= len(turns):
			turn_index = 0
			
		mm = randf(25, 35)
		user_data[user.lower()]["money"] += mm
		
		user_data[user.lower()]["stats"]["Kills"] += 1

		if not bot:
			return ["(+{money}) {user} is now dead! He's out of the game! Rejoin?".format(money=mm, user=target)]
			
		return ["{} killed {} with {}! He's out of the game!".format(capsname[user.lower()], weapon, capsname[target.lower()])]
		
	if user_data[target.lower()]["fungushealth"] < 1 and user_data[target.lower()]["mush"]:
		user_data[user.lower()]["money"] += 50
		user_data[target.lower()]["mush"] = False
		user_data[target.lower()]["immune"] = 3
		
		user_data[user.lower()]["stats"]["Cures"] += 1
		
		return ["(+50) {} is not a mush anymore!".format(target)]
		
	if user_data[target.lower()]["mush"] != user_data[user.lower()]["mush"]:
		user_data[user.lower()]["money"] += randf(4.75, 10)
		
	if not user_data[target.lower()]["mush"]:
		if not bot:
			return ["Dealt {} damage into the target!".format((realdamage if gun["drainhealth"] else 0))]
		
		else:
			return ["{} dealt {} damage into {}!".format(capsname[user.lower()], (realdamage if gun["drainhealth"] else 0), capsname[target.lower()])]
		
	else:
		if not bot:
			return ["Dealt {} damage into the target plus {} damage to the fungus!".format((realdamage if gun["drainhealth"] else 0), (realfdamage if gun["drainfungushealth"] else 0))]
			
		else:
			return ["{} dealt {} damage into {} plus {} damage to it's fungus!".format(capsname[user.lower()], (realdamage if gun["drainhealth"] else 0), capsname[target.lower()], (realfdamage if gun["drainfungushealth"] else 0))]
	
def pass_turn():
	global turns
	global turn_index
	
	turn_index += 1
	
	if turn_index >= len(turns):
		turn_index = 0
	
def best_weapon(player, trying_cure=False):
	if trying_cure:
		order = ["gas", "serum", "rockox", "machinegun", "pistol"]
	
	else:
		order = ["rockox", "machinegun", "gas", "pistol", "serum"]

	try:
		if user_data[player.lower()]["mush"]:
			return max([x for x, y in user_data[player.lower()]["weapons"].items() if y], key=lambda x: 0 if x not in order else order.index(x) + 1)
			
		else:
			return max([x for x, y in user_data[player.lower()]["weapons"].items() if y], key=lambda x: 0 if x not in [y for y in order if y not in ("serum", "gas")] else order.index(x) + 1)
			
	except (IndexError, ValueError):
		return None
	
class OneSideCatching(BaseException):
	pass
	
def check_bot_turn(top_level=True):
	global turns
	global turn_index
	global user_data

	bp = turns[turn_index].lower()
	
	user_data[bp]["stats"]["Turns Survived"] += 1
	
	if not user_data[bp]["bot"]:
		return (["It's now {}'s turn!".format(capsname[turns[turn_index]])] if top_level else [])
		
	messages = []
	
	bd = user_data[bp]
	
	turn_passed = False

	weapons = set()
	
	while True:
		if len([x for x, y in user_data.items() if y["mush"]]) == 0 or len([x for x, y in user_data.items() if not y["mush"]]) == 0:
			if not top_level:
				raise OneSideCatching
				
			else:
				return ["{}Mushes Already Won!".format(("Non-" if False in [y["mush"] for x, y in user_data.items()] else ""))]
	
		if bd["mush"]:
			try:
				mtarget = choice([x for x, y in user_data.items() if not y["mush"]])
				teammate = choice([x for x, y in user_data.items() if y["mush"]])
				
				print mtarget, teammate
				
			except ValueError:
				turn_passed = True
				break
				
			if mtarget == None:
				turn_passed = True
				break
				
			if bd["fungushealth"] < 35:
				mfh = mfh = randf(20, 50)
			
				user_data[bp]["fungushealth"] += mfh
			
				messages.append("{} ate something healthy! +{} fungus health!".format(capsname[bp], mfh))
			
				break
				
			elif bd["health"] < 47.5:
				if not bd["weapons"]["healgun"] and weapon_data["healgun"]["cost"] < bd["money"]:
					user_data[bp]["weapons"]["healgun"] = True
					messages.append("{} bought a healgun!".format(capsname[bp]))
			
				if bd["ammo"]["heal"] <= 0 and ammo_data["heal"]["cost"] < bd["money"]:
					messages.append("{} bought heal ammo!".format(capsname[bp]))
					user_data[bp]["ammo"]["heal"] += ammo_data["heal"]["amount"]
					user_data[bp]["money"] += ammo_data["heal"]["cost"]
			
				messages.append("{} shot himself a healgun!".format(capsname[bp]))
				messages += shoot(capsname[bp], bp, "healgun", True)
				
			elif user_data[teammate]["health"] < 40 or user_data[teammate]["fungushealth"] < 35:
				if not bd["weapons"]["healgun"] and weapon_data["healgun"]["cost"] < bd["money"]:
					user_data[bp]["weapons"]["healgun"] = True
					messages.append("{} bought a healgun!".format(capsname[bp]))
			
				if bd["ammo"]["heal"] <= 0 and ammo_data["heal"]["cost"] < bd["money"]:
					messages.append("{} bought heal ammo!".format(capsname[bp]))
					user_data[bp]["ammo"]["heal"] += ammo_data["heal"]["amount"]
					user_data[bp]["money"] += ammo_data["heal"]["cost"]
			
				messages.append("{} shot {} a healgun!".format(capsname[bp], capsname[teammate]))
				messages += shoot(capsname[bp], teammate, "healgun", True)
				
			elif user_data[mtarget]["immune"] > 1.85 and user_data[bp]["weapons"]["aidsgun"]:
				while True:
					if bd["ammo"]["aids"] <= 0 and ammo_data["aids"]["cost"] < bd["money"]:
						messages.append("{} bought aids ammo!".format(capsname[bp]))
						user_data[bp]["ammo"]["aids"] += ammo_data["aids"]["amount"]
						user_data[bp]["money"] += ammo_data["aids"]["cost"]
						
					elif bd["ammo"]["aids"] <= 0:
						break
				
					messages.append("{} shot {} at {}!".format(capsname[bp], "aidsgun", capsname[mtarget]))
					messages += shoot(capsname[bp], mtarget, "aidsgun", True)
					
					break
				
			elif not user_data[bp]["weapons"]["aidsgun"]:
				random_weapon = "aidsgun"
			
				user_data[bp]["money"] -= weapon_data[random_weapon]["cost"]
				user_data[bp]["weapons"][random_weapon] = True
				
				messages.append("{} bought {}!".format(capsname[bp], random_weapon))
			
				if user_data[mtarget]["immune"] > 1.85 and user_data[bp]["weapons"]["aidsgun"]:
					messages.append("{} shot {} at {}!".format(capsname[bp], "aidsgun", capsname[mtarget]))
					messages += shoot(capsname[bp], mtarget, "aidsgun", True)
				
			elif user_data[mtarget]["immune"] < 1.2 and user_data[bp]["spores"] and user_data[bp]["spores"] > 0:
				user_data[bp]["spores"] -= 1
				user_data[mtarget]["immune"] -= 1
				
				if user_data[mtarget]["immune"] <= 0:
					user_data[mtarget]["fungushealth"] = 72
					user_data[mtarget]["mush"] = True
					user_data[bp]["money"] += 35
					user_data[bp]["stats"]["Infections"] += 1
					messages.append("{} infected {}! Now {} is a mush!".format(capsname[bp], capsname[mtarget], capsname[mtarget]))
				
				else:
					messages += ["{} spiked {}! But it'll take more than that! Immune down to {} now!".format(capsname[bp], capsname[mtarget], user_data[mtarget]["immune"])]
				
			elif user_data[bp]["spores"] <= 0:	
				user_data[bp]["spores"] += 1
				messages += ["Extracted a spore! (now with {})".format(user_data[bp]["spores"])]
				
			elif user_data[mtarget]["health"] < 21 and best_weapon(bp) != None:
				if bd["ammo"][weapon_data[best_weapon(bp)]["ammotype"]] <= 0 and ammo_data[weapon_data[best_weapon(bp)]["ammotype"]]["cost"] < bd["money"]:
					user_data[bp]["ammo"][weapon_data[best_weapon(bp)]["ammotype"]] += ammo_data[weapon_data[best_weapon(bp)]["ammotype"]]["amount"]
					user_data[bp]["money"] -= ammo_data[weapon_data[best_weapon(bp)]["ammotype"]]["cost"]
					user_data[bp]["stats"]["Buys"] += 1
					messages.append("{} bought {} ammo!".format(weapon_data[best_weapon(bp)]["ammotype"]))
					break
					
				messages.append("{} shot {} at {}! Shots Fired!".format(capsname[bp], best_weapon(bp), capsname[mtarget]))
				messages += shoot(capsname[bp], mtarget, best_weapon(bp), True)
				
			elif best_weapon(bp) == None:
				fail = False
			
				while True:
					random_weapon = choice([x for x in weapon_data.keys() if x not in ("healgun", "serum", "gas")])
					
					if weapon_data[random_weapon]["cost"] > bd["money"] or random_weapon in weapons:
						weapons.add(random_weapon)
						
						print weapons
						
						if len(weapons & set(weapon_data.keys())) == len(weapon_data.keys()):
							fail = True
							break
						
						continue

					break
					
				if fail:
					turn_passed = True
					break
					
				print user_data[bp]["money"],
				user_data[bp]["money"] -= weapon_data[random_weapon]["cost"]
				print user_data[bp]["money"]
				user_data[bp]["weapons"][random_weapon] = True
				user_data[bp]["stats"]["Buys"] += 1
				
				messages.append("{} bought {}!".format(capsname[bp]), random_weapon)
				continue
				
			else:
				turn_passed = True
				
		else:
			try:
				mtarget = choice([x for x, y in user_data.items() if y["mush"]])
				teammate = choice([x for x, y in user_data.items() if not y["mush"]])
				
			except ValueError:
				turn_passed = True
				break
				
			if mtarget == None:
				turn_passed = True
				break
			
			elif user_data[mtarget]["fungushealth"] < 45 and best_weapon(bp, True) != None:
				messages.append("{} shot {} at {}! Shots Fired!".format(capsname[bp], best_weapon(bp, True), capsname[mtarget]))
				messages += shoot(capsname[bp], mtarget, best_weapon(bp, True))
				
			elif user_data[mtarget]["health"] < 58.25 and best_weapon(bp) != None:
				messages.append("{} shot {} at {}! Shots Fired!".format(capsname[bp], best_weapon(bp, False), capsname[mtarget]))
				messages += shoot(capsname[bp], mtarget, best_weapon(bp, True))
				
			elif bd["health"] < 47.5:
				if not bd["weapons"]["healgun"] and weapon_data["healgun"]["cost"] < bd["money"]:
					user_data[bp]["weapons"]["healgun"] = True
					messages.append("{} bought a healgun!".format(capsname[bp]))
			
				if bd["ammo"]["heal"] <= 0 and ammo_data["heal"]["cost"] < bd["money"]:
					messages.append("{} bought heal ammo!".format(capsname[bp]))
					user_data[bp]["ammo"]["heal"] += ammo_data["heal"]["amount"]
					user_data[bp]["money"] += ammo_data["heal"]["cost"]
			
				messages.append("{} shot himself a healgun!".format(capsname[bp]))
				messages += shoot(capsname[bp], bp, "healgun", True)
				
			elif user_data[teammate]["health"] < 40:
				if not bd["weapons"]["healgun"] and weapon_data["healgun"]["cost"] < bd["money"]:
					user_data[bp]["weapons"]["healgun"] = True
					messages.append("{} bought a healgun!".format(capsname[bp]))
			
				if bd["ammo"]["heal"] <= 0 and ammo_data["heal"]["cost"] < bd["money"]:
					messages.append("{} bought heal ammo!".format(capsname[bp]))
					user_data[bp]["ammo"]["heal"] += ammo_data["heal"]["amount"]
					user_data[bp]["money"] += ammo_data["heal"]["cost"]
			
				messages.append("{} shot {} a healgun!".format(capsname[bp], capsname[teammate]))
				messages += shoot(capsname[bp], teammate, "healgun", True)
				
			elif user_data[bp]["immune"] < 2.0:
				old_immune = user_data[bp]["immune"]
				user_data[bp]["immune"] += randint(72, 132) * 0.01
				messages.append("{} ate something healthy! Mmmmm, +{} immune on Rehermann scale!".format(capsname[bp], user_data[bp]["immune"] - old_immune))
			
			elif best_weapon(bp) != None:
				if bd["ammo"][weapon_data[best_weapon(bp)]["ammotype"]] <= 0:
					user_data[bp]["ammo"][weapon_data[best_weapon(bp)]["ammotype"]] += ammo_data[weapon_data[best_weapon(bp)]["ammotype"]]["amount"]
					user_data[bp]["money"] -= ammo_data[weapon_data[best_weapon(bp)]["ammotype"]]["cost"]
					messages.append("{} bought {} ammo!".format(capsname[bp], weapon_data[best_weapon(bp)]["ammotype"]))
					break
			
				if user_data[mtarget]["fungushealth"] > user_data[mtarget]["health"] * 1.725:
					messages.append("{} shot {} at {}! Shots Fired!".format(capsname[bp], best_weapon(bp, False), capsname[mtarget]))
					messages += shoot(capsname[bp], mtarget, best_weapon(bp, True))
			
				else:
					messages.append("{} shot {} at {}! Shots Fired!".format(capsname[bp], best_weapon(bp, True), capsname[mtarget]))
					messages += shoot(capsname[bp], mtarget, best_weapon(bp), True)
				
			else:
				fail = False
			
				if percent_chance(50):
					while True:
						random_weapon = choice([x for x in weapon_data.keys() if x not in ("aidsgun", "healgun")])
						
						if weapon_data[random_weapon]["cost"] > bd["money"] or random_weapon in weapons:
							weapons.add(random_weapon)
							
							print weapons
							
							if len(weapons & set(weapon_data.keys())) == len(weapon_data.keys()):
								fail = True
								break
							
							continue

						break
						
					if fail:
						turn_passed = True
						break
						
				else:
					random_weapon = "gas"
					
					if weapon_data[random_weapon]["cost"] < bd["money"] or random_weapon in weapons:
						turn_passed = True
						break
					
				user_data[bp]["money"] -= weapon_data[random_weapon]["cost"]
				user_data[bp]["weapons"][random_weapon] = True
				user_data[bp]["stats"]["Buys"] += 1
				
				messages.append("{} bought {}!".format(capsname[bp], random_weapon))
				continue
			
		break
			
	pass_turn()
	
	if turn_passed:
		messages.append("{} passed the turn!".format(capsname[bp]))
	
	try:
		messages += check_bot_turn(False)
		
	except OneSideCatching:
		return ["{}Mushes Win!".format(("Non-" if False in [y["mush"] for x, y in user_data.items()] else ""))]
	
	if top_level and condense_bot_messages:
		msgs = messages
		mm = []
		messages = []
		
		for x in msgs:
			mm.append(x)
			
			if len(" | ".join(mm)) > 300:
				messages.append(" | ".join(mm))
				mm = []
				
		if messages[-1] != " | ".join(mm):
			messages.append(" | ".join(mm))
		
	return messages
	
@easy_bot_command("smw_statistics")
def get_statistics(message, raw):
	if raw:
		return

	try:
		target = message["arguments"][1]
		tn = target.lower()
		
	except IndexError:
		target = tn = ""
	
	if tn in turns:
		return "{} ({}Mush) Game Statistics: ".format(target, ("Non-" if not user_data[tn]["mush"] else "")) + "; ".join(["{}: {}".format(x, y) for x, y in user_data[tn]["stats"].items()])
		
	else:
		result = ["Match Statistics: "] + ["{} ({}Mush) Game Statistics: ".format(capsname[tn], ("Non-" if not user_data[tn]["mush"] else "")) + "; ".join(["{}: {}".format(x, y) for x, y in user_data[tn]["stats"].items()]) for tn in turns]
		
		if result:
			return result
			
		else:
			return "Error: No one in the match!"
			
@easy_bot_command("smw_leaderboard")
def statistical_leaderboard(message, raw):
	if raw:
		return
		
	parts = ["OFFICIAL LEADERBOARD!"]
	
	leaderboard = {
		"\'Lamp\' (to cast light, y'know)": (sorted(user_data.items(), key=lambda x: x[1]["stats"]["Infections"]), "enlightenings", "Infections"),
		"Spender": (sorted(user_data.items(), key=lambda x: x[1]["stats"]["Buys"]), "buys", "Buys"),
		"Assassin": (sorted(user_data.items(), key=lambda x: x[1]["stats"]["Kills"]), "kills", "Kills"),
		"Survivor": (sorted(user_data.items(), key=lambda x: x[1]["stats"]["Turns Survived"]), "turns without passing away", "Turns Survived"),
		"AIDS user... kinda": (sorted(user_data.items(), key=lambda x: x[1]["stats"]["AIDS Overdoses"]), "overdoses caused by him", "AIDS Overdoses"),
		"Medic": (sorted(user_data.items(), key=lambda x: x[1]["stats"]["Cures"]), "\'unmushings\' (blergh)", "Cures"),
	}
		
	print leaderboard["Spender"]
	
	for rankee, ranking in leaderboard.items():
		print ranking, "\n\n\n"
		parts.append("Best {}: {} with {} {}!".format(rankee, capsname[ranking[0]], user_data[ranking[0]]["stats"][ranking[2]], ranking[1]))
		
	return " | ".join(parts)
	
@easy_bot_command("smw_addbots")
def smw_add_a_bot(message, raw):
	global user_data
	global num_bots
	
	if raw:
		return

	names = []
		
	try:
		bots = int(message["arguments"][1])
		
	except (IndexError, ValueError):
		bots = 1
		
	if bots + num_bots > 40:
		bots = 40 - num_bots
		
	if bots == 0:
		return "Error: Max limit reached!"
		
	num_bots += bots
		
	for i in xrange(bots):
		is_mush = percent_chance(48)
		name = choice([x.strip("\n") for x in open("botnames.txt").readlines()])
		
		if name.lower() in user_data.keys():
			name += str(user_data.keys().count(name.lower()))
		
		print name
			
		names.append(name)
		turns.append(name.lower())
		capsname[name.lower()] = name	
		user_data[name.lower()] = {
			"host": ".!.@.",
			"money": 30,
			"mush": is_mush,
			"spores": 6,
			"immune": 3,
			"ammo": {x: y["defaultvalue"] for x, y in ammo_data.items()},
			"weapons": {x: False for x in weapon_data.keys()},
			"health": 100,
			"bot": True,
			"fungushealth": 72,
			"stats": {
				"Kills": 0,
				"AIDS Overdoses": 0,
				"Infections": 0,
				"Buys": 0,
				"Turns Survived": 0,
				"Cures": 0,
			},
	}
	
	return "Added {} bots ({}) to the game!".format(bots, ", ".join(names))

@easy_bot_command("smw_eat")
def smw_eat_something_healthy(message, raw):
	global user_data
	global turns
	global turn_index

	if raw:
		return
		
	user = message["nickname"]
		
	if user.lower() not in user_data.keys():
		return ["Eat your vegetables and brush after every meal! ;)"]
		
	if user.lower() != turns[turn_index]:
		return "Hey! Eat when it's your turn! :P"
		
	if len(user_data.keys()) < 2:
		return "Mmmmmm! That's appreciable, indeed."	
	
	if user_data[user.lower()]["mush"]:
		mfh = randf(20, 50)
		user_data[user.lower()]["fungushealth"] += mfh
		
		turn_index += 1
		
		if turn_index >= len(turns):
			turn_index = 0
		
		return ["Mmmmmmm! +{} fungus health!".format(mfh)]
	
	old_immune = user_data[user.lower()]["immune"]
	user_data[user.lower()]["immune"] += randint(72, 132) * 0.01
	
	turn_index += 1
		
	if turn_index >= len(turns):
		turn_index = 0
	
	return ["Mmmmmmmmmmm! +{} immune power in Rehermann scale!".format(user_data[user.lower()]["immune"] - old_immune)] + check_bot_turn()

@easy_bot_command("smw_findspore")
def smw_search_for_spores(message, raw):
	if raw:
		return
		
	user = message["nickname"]
	
	if user.lower() not in user_data.keys():
		return ["Join the game first using ||smw_join !"]
		
	if not percent_chance(62):
		return ["No spore found!"]
		
	if user_data[user.lower()]["mush"]:
		user_data[user.lower()]["spores"] += 1
		pass_turn()
		return ["Found a random spore! Absorbing... Now you have {} spores!".format(user_data[user.lower()]["spores"]) + "It's now {}'s turn!".format(capsname[turns[turn_index]])] + check_bot_turn()
		
	if percent_chance(72):
		user_data[user.lower()]["fungushealth"] = 72
		user_data[user.lower()]["mush"] = True
		return ["Found a spore... but wait, was that meant to happen? Now you are... a mush!"]
		
	else:
		return ["You found a spore! But wait... why were you looking for spores?", "Do you want to plant champignons or didn't you know the danger of this?"]

		

@easy_bot_command("smw_turns")
def turn_list(message, raw):
	global turns
	
	if raw:
		return
		
	check_bot_turn()
		
	return ["Turn queue: " + ", ".join([capsname[x] for x in turns])] + (["Current: " + capsname[turns[turn_index]]] if turns else [])
		
@easy_bot_command("smw_join")
def join_warzone_stats(message, raw):
	global turn_index
	global turns

	if raw:
		return

	user = message["nickname"]
	is_mush = percent_chance(48)
	
	if user.lower() in user_data.keys():
		return ["You already joined the game! To quit (suicide), use ||smw_quit ."]
		
	turns.append(user.lower())
	capsname[user.lower()] = user
		
	user_data[user.lower()] = {
		"host": message["host"],
		"money": 30,
		"mush": is_mush,
		"spores": 6,
		"immune": 3,
		"ammo": {x: y["defaultvalue"] for x, y in ammo_data.items()},
		"weapons": {x: False for x in weapon_data.keys()},
		"health": 100,
		"bot": False,
		"fungushealth": 72,
		"stats": {
			"Kills": 0,
			"AIDS Overdoses": 0,
			"Infections": 0,
			"Buys": 0,
			"Turns Survived": 0,
			"Cures": 0,
		},
	}
	
	return ["You were added to the game! You are{}a mush!".format((" not " if not is_mush else " "))] + check_bot_turn()

@easy_bot_command("smw_givemoney")
def give_someone_dollars(message, raw):
	if raw:
		return
		
	user = message["nickname"]
		
	try:
		target = message["arguments"][1]
		
	except IndexError:
		return ["Give money to who?"]
		
	try:
		amount = int(message["arguments"][2])
		
	except IndexError:
		return ["Give how )uch money?"]
		
	except ValueError:
		return ["Invalid money literal!"]
		
	if user.lower() not in user_data.keys():
		return ["Join first using ||smw_join !"]
		
	if target.lower() not in user_data.keys():
		return ["Uh? Give money to who?"]
		
	if user_data[user.lower()]["money"] < amount:
		return "Not enough money!"
	
	user_data[user.lower()]["money"] -= amount
	user_data[target.lower()]["money"] += amount
		
	return ["{} gave {} bucks to {}!".format(user, target, amount)]
	
@easy_bot_command("smw_players")
def smw_player_list(message, raw):
	if raw:
		return
		
	player_list = []
	mini_player_list = []
	
	print user_data
	
	for player in user_data.keys():
		mini_player_list.append("{} ({} | {}Bot)".format(capsname[player].encode('utf-8'), ("Mush" if user_data[player]["mush"] else "Not Mush"), ("Not a " if not user_data[player]["bot"] else "")))
		
		if len(mini_player_list) % 30 == 0:
			player_list.append(", ".join(mini_player_list))
			mini_player_list = []
			
	if len(player_list) < 1 or player_list[-1] != mini_player_list[-1]:
		player_list.append(", ".join(mini_player_list))
		
	return ["There are {} players: ".format(len(user_data)) + player_list[0]] + player_list[1:]
	
@easy_bot_command("smw_rebalance", True)
def smw_balance_teams(message, raw):
	global user_data

	if raw:
		return
		
	mushies = len([user for user in user_data.values() if user["mush"]])
	humans = len([user for user in user_data.values() if not user["mush"]])
	cured = []
	
	if mushies == humans:
		return ["Game already balanced!"]
	
	if mushies > 0:
		while True:
			mushies = len([user for user in user_data.values() if user["mush"]])
			humans = len([user for user in user_data.values() if not user["mush"]])
		
			if mushies > humans and ((mushies + humans) % 2 == 0 or mushies > humans + 1):
				usa, item = choice(user_data.items())
				user_data[usa]["mush"] = False
				user_data[usa]["immune"] = 3
				cured.append(usa)
				continue
		
			if not cured:
				return ["Game already balanced!"]
			
			break
		
		return ["Unmushed (for balancement): " + ", ".join(cured)]
		
	else:
		while True:
			mushies = len([user for user in user_data.values() if user["mush"]])
			humans = len([user for user in user_data.values() if not user["mush"]])
			
			if humans > mushies and ((humans + mushies) % 2 == 0 or humans > mushies + 1):
				usa, item = choice(user_data.items())
				user_data[usa]["mush"] = True
				cured.append(usa)
				continue
			
			if not cured:
				return ["Game already balanced!"]
			
			break		
			
		return ["Mushed (for balancement): " + ", ".join(cured)]
	
@easy_bot_command("smw_shoot")
def smw_shoot(message, raw):
	global turn_index
	global turns

	if raw:
		return
	
	if len(message["arguments"]) < 3:
		return ["Syntax: smw_shoot <target> <weapon>"]
	
	user = message["nickname"]
	target = message["arguments"][1]
	weapon = message["arguments"][2]
	
	if user.lower() not in user_data.keys():
		return ["Join the game first using ||smw_join !"]
	
	if target.lower() not in user_data.keys():
		return ["Who is that? I don't think he's aboard either."]
	
	if weapon not in weapon_data.keys():
		return ["Uh, did you invent that shiny new weapon?"]
		
	if not user_data[user.lower()]["weapons"][weapon]:
		return ["You don't have that weapon, sorry!"]
	
	shoot_succesfull = True
	
	result = [shoot(user, target, weapon)]
	
	if not shoot_succesfull:
		pass_turn()
		
	return result + check_bot_turn()
		
@easy_bot_command("smw_extract")
def smw_extract_spore(message, raw):
	global turn_index
	global turns

	if raw:
		return
	
	user = message["nickname"]
		
	if user.lower() not in user_data.keys():
		return ["Join the game first using ||smw_join !"]
		
	if not user_data[user.lower()]["mush"]:
		return ["You are not one of these yet! Hey, do you want to be one?..."]
		
	if user_data[user.lower()]["spores"] >= 15:
		return ["Max spores reached! (15)"]

	try:
		if turns[turn_index] != user.lower().lower():
			return ["Hey! It's not your turn! Stop breaking the queue!"]
			
	except IndexError:
		return ["Nobody's playing! There's no turn to pass!"]
		
	turn_index += 1
	
	print turn_index
	
	if turn_index >= len(turns):
		turn_index = 0
		
	print turn_index
		
	user_data[user.lower()]["spores"] += 1
	return ["Extracted a spore! (now with {})".format(user_data[user.lower()]["spores"])] + check_bot_turn()
	
@easy_bot_command("smw_spike")
def spike_user_with_spore(message, raw):
	global turn_index
	global turns

	if raw:
		return
		
	user = message["nickname"]
	
	if user.lower() not in user_data.keys():
		return ["Join the game first using ||smw_join !"]
	
	try:
		target = message["arguments"][1]
		
	except IndexError:
		return ["Syntax: smw_spike <target to mushify/infect/enlighten/gah>"]
	
	if target.lower() not in user_data.keys():
		return ["Who is your target? Is it even aboard?"]
		
	if not user_data[user.lower()]["mush"]:
		return ["Where do you think you'll get spores from?"]
		
	if user_data[target.lower()]["mush"]:
		return ["He's already one!"]
		
	if user_data[user.lower()]["spores"] < 1:
		return ["You're out of spores!"]
		
	try:
		if turns[turn_index] != user.lower():
			return ["Hey! It's not your turn! Stop breaking the queue!"]
			
	except IndexError:
		return ["Nobody's playing! There's no turn to pass!"]
		
	turn_index += 1
	
	if turn_index >= len(turns):
		turn_index = 0
		
	user_data[user.lower()]["spores"] -= 1
	user_data[target.lower()]["immune"] -= 1
	
	if user_data[target.lower()]["immune"] <= 0:
		user_data[target.lower()]["fungushealth"] = 72
		user_data[target.lower()]["mush"] = True
		user_data[user.lower()]["money"] += 35
		user_data[user.lower()]["stats"]["Infections"] += 1
		
		return ["(+35) Infection succesful! Now {} is a mush!".format(target)] + check_bot_turn()
	
	return ["Spiking succesful! But, he will take more than that; his immune system is now already {} though!".format(user_data[target.lower()]["immune"])] + check_bot_turn()
	
@easy_bot_command("smw_hug")
def smw_hugging(message, raw):
	if raw:
		return
		
	player = message["nickname"].lower()
	
	try:
		target = message["arguments"][1].lower()
		
	except IndexError:
		return ["You are huggy! Hug who?"]
	
	if player not in user_data.keys():
		return ["Join first using ||smw_join !"]
		
	if target not in user_data.keys():
		return ["Uh? Hug who? Is he even joined?"]
	
	real_hug = user_data[player]["mush"] != user_data[target]["mush"]
	
	if not real_hug:
		return ["{} hugs {}! They are indeed real friends.".format(player, target)]
		
	else:
		return ["{0} hugs {1}! {0} really wants to be friends with him, despite the \'differences\'...".format(player, target)]
	
@easy_bot_command("smw_turn")
def smw_whos_turn(message, raw):
	if raw:
		return
		
	if len(turns) < 1:
		return "No one's turn! Who's playing?"
		
	return "It's now {}'s turn!".format(capsname[turns[turn_index]])
	
@easy_bot_command("smw_pass")
def smw_pass_turn(message, raw):
	global turn_index
	global turns

	if raw:
		return
		
	user = message["nickname"]
		
	try:
		if turns[turn_index] != user.lower().lower():
			return ["Hey! It's not your turn! Stop breaking the queue!"]
			
	except IndexError:
		return ["Nobody's playing! There's no turn to pass!"]
		
	turn_index += 1
	
	if turn_index >= len(turns):
		turn_index = 0
		
	return ["Turn passed! It's now {}'s turn!".format(capsname[turns[turn_index]])] + check_bot_turn()
	
@easy_bot_command("smw_quit")
def smw_quit(message, raw):
	global turns
	global turn_index

	if raw:
		return
		
	user = message["nickname"]
	
	if not user.lower() in user_data.keys():
		return ["You are not joined either!"]
		
	user_data.__delitem__(user.lower())
	
	if turns[turn_index] == user:
		turn_index += 1
		
	if turn_index >= len(turns):
		turn_index = 0
	
	for i, x in enumerate(turns):
		if x == user.lower():
			turns.pop(i)
	
	return ["Suicide succesful! :3"]
	
@easy_bot_command("smw_surrender")
def smw_surrender(message, raw):
	if raw:
		return
		
	user = message["nickname"]
	
	if user.lower() not in user_data.keys():
		return "What are you surrendering from?"
	
	data = user_data[user.lower()]
	
	if data["mush"]:
		return "You could surrender to evil, but it'd not be good for you..."
		
	return [
		"You surrender. You want your friends back. You are fed of doing this. You aren't meant to be evil. You are just scared.",
		"Suddenly you feel like something's watching you. Like a heart has been touched, at last."
	]
	
@easy_bot_command("smw_status")
def smw_user_status(message, raw):
	if raw:
		return
		
	user = message["nickname"]
	
	if user.lower() not in user_data.keys():
		return ["Join the game first using ||smw_join !"]
	
	return " | ".join([
		"{} Status:".format(user),
		"You have {} money.".format(user_data[user.lower()]["money"]),
		"You are{}a mush.".format((" not " if not user_data[user.lower()]["mush"] else " ")),
		"You have {} health{}.".format(user_data[user.lower()]["health"], (" ({} fungus health)".format(user_data[user.lower()]["fungushealth"]) if user_data[user.lower()]["mush"] else "")),
		"You have immune system of {} in the Rehermann scale.".format(user_data[user.lower()]["immune"]),
		("You have the following weapons: " + ", ".join(["{} ({})".format(weapon, user_data[user.lower()]["ammo"][weapon_data[weapon]["ammotype"]]) for weapon, data in user_data[user.lower()]["weapons"].items() if data]) if True in user_data[user.lower()]["weapons"].values() else "You have no guns! :("),
		("" if not user_data[user.lower()]["mush"] else 
		"You have {} spores.".format(user_data[user.lower()]["spores"]))
	])
		
@easy_bot_command("smw_getstatus")
def smw_get_user_status(message, raw):
	if raw:
		return
		
	try:
		target = message["arguments"][1]
		
	except IndexError:
		return ["Syntax: smw_getstatus <user>"]
		
	if target.lower() not in user_data.keys():
		return ["Error: Target didn't join!"]
	
	return " | ".join([
		"{} Status:".format(target),
		"He/she has {} money.".format(user_data[target.lower()]["money"]),
		"He/she is{}a mush.".format((" not " if not user_data[target.lower()]["mush"] else " ")),
		"He/she has {} health{}.".format(user_data[target.lower()]["health"], (" ({} fungus health)".format(user_data[target.lower()]["fungushealth"]) if user_data[target.lower()]["mush"] else "")),
		"He/she has immune system of {} in the Rehermann scale.".format(user_data[target.lower()]["immune"]),
		("He/she has the following weapons: " + ", ".join(["{} ({})".format(weapon, user_data[target.lower()]["ammo"][weapon_data[weapon]["ammotype"]]) for weapon, data in user_data[target.lower()]["weapons"].items() if data]) if True in user_data[target.lower()]["weapons"].values() else "He/she has got no guns!"),
	] + ([] if not user_data[target.lower()]["mush"] else [
		"He/she has {} spores.".format(user_data[target.lower()]["spores"])
	]))
	
@easy_bot_command("smw_savedata", True)
def save_user_data(message, raw):
	global user_data
	global turns
	global capsname

	if raw:
		return
	
	open("smwuserdata.json", "w").write(dumps([user_data, turns, capsname]))
	return "User data saved succesfully!"
	
@easy_bot_command("smw_loaddata", True)
def load_user_data(message, raw):
	global user_data
	global turns
	global capsname
	
	if raw:
		return
		
	data = load(open("smwuserdata.json"))
	user_data = data[0]
	turns = data[1]
	capsname = data[2]
	
	return "User data loaded succesfully!"
	
@easy_bot_command("smw_about")
def smw_about(message, raw):
	if raw:
		return
		
	return [
		"Sentient Mushes: Warzone (c) 2016 Gustavo Ramos \"Gustavo6046\" Rehermann.",
		"Source code is MIT License. For more info please check LICENSE.txt in the top folder .",
		"Source code at: https://www.github.com/Gustavo6046/GusBot-2",
		"Sentient Mushes series; Inspired by another Twinoidian game."
	]
	
@easy_bot_command("smw_buygun")
def smw_buy_a_big_weapon(message, raw):
	if raw:
		return
		
	user = message["nickname"]
	
	if not user.lower() in user_data.keys():
		return ["Join the game first using ||smw_join !"]
		
	try:
		weapon = message["arguments"][1]
		
	except IndexError:
		return ["Syntax: smw_buygun <gun's name>"]
		
	money = user_data[user.lower()]["money"]
	
	if weapon not in weapon_data.keys():
		return ["You can't buy your inventions; they're already yours!", "Well, maybe of your imagination, that is... :3"]
		
	try:
		if user_data[user.lower()]["weapons"][weapon]:
			return ["You already have that weapon!"]
		
	except KeyError:
		pass
		
	if user_data[user.lower()]["money"] < weapon_data[weapon]["cost"]:
		return ["Too little money!"]
		
	user_data[user.lower()]["stats"]["Buys"] += 1
	user_data[user.lower()]["money"] -= weapon_data[weapon]["cost"]
	user_data[user.lower()]["weapons"][weapon] = True
	return "Bought weapon succesfully!"
	
@easy_bot_command("smw_buyammo")
def smw_buy_some_ammo(message, raw):
	if raw:
		return
		
	user = message["nickname"]
	
	if not user.lower() in user_data.keys():
		return ["Join the game first using ||smw_join !"]
		
	try:
		ammo_type = message["arguments"][1]
		
	except IndexError:
		return ["Syntax: smw_buyammo <ammo type>"]
		
	money = user_data[user.lower()]["money"]
	
	if ammo_type not in ammo_data.keys():
		return ["You can't buy your inventions; they're already yours!", "Well, maybe of your imagination, that is... :3"]
		
	if user_data[user.lower()]["money"] < ammo_data[ammo_type]["cost"]:
		return ["Too little money!"]
		
	user_data[user.lower()]["stats"]["Buys"] += 1
	user_data[user.lower()]["money"] -= ammo_data[ammo_type]["cost"]
	user_data[user.lower()]["ammo"][ammo_type] += ammo_data[ammo_type]["amount"]
	return "Bought ammunition succesfully!"
	
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
	
@easy_bot_command("smw_hide")
def hide_frowning_as_always(message, raw):
	if raw:
		return
		
	user = message["nickname"]
	
	if user.lower() not in user_data.keys():
		return ["You hide... but why? Are you really hiding or did you mean to hide inminigame?"]
	
	if user_data[user.lower()]["mush"]:
		return ["You hide somewhere, frowning. You want to get out of the confusion.", "You didn't want to be enemy of anyone.", "Suddenly, you realize. Hearts are emotionally weak. With this in mind, there must be a way out!"]
	
	return ["You hide somewhere, frowning. You miss your friends.", "Maybe if you show your sadness and maybe surrender, since you might not be able to fight back..."]
	
@bot_command("GETNICKCHANGES0", False, False, False, True)
def get_nick_changes(message, connector, index, raw):
	global turns
	
	if not raw:
		return

	try:
		if message["raw"].split(" ")[1].upper() != "NICK":
			return
			
	except IndexError:
		return
	
	old_nick = message["raw"].split("!")[0]
	
	try:
		new_nick = message["raw"].split(" ")[2]
		
	except IndexError:
		return
		
	print "{} -> {}".format(old_nick, new_nick)
		
	while True:
		if old_nick not in user_data.keys():
			break
			
		user_data[new_nick] = user_data[old_nick]
		user_data.__delitem__(old_nick)
		
		break
	
	for i, user in enumerate(turns):
		if user == old_nick:
			turns.pop(i)
			turns.insert(i, new_nick)
	
@easy_bot_command("smw_resetmatch", True)
def reset_smw_match(message, raw):
	global user_data
	global turns
	global turn_index

	if raw:
		return
		
	user_data = {}
	turns = []
	turn_index = 0
		
	return ["Reset with success!", "...Anyone gonna join now?"]
	
@easy_bot_command("smw_cost")
def get_smw_gun_cost(message, raw):
	if raw:
		return
		
	object = " ".join(message["arguments"][1:])
		
	if object in ammo_data.keys():
		return ["That ammo costs {}.".format(ammo_data[object]["cost"])]
		
	elif object in weapon_data.keys():
		return ["That weapon costs {}.".format(weapon_data[object]["cost"])]
		
	elif object in user_data.keys():
		return ["A friendship is for free! :D <3"]
		
	else:
		return ["What's that?"]
		
@easy_bot_command("smw_kick", True)
def kick_smw_player(message, raw):
	global turn_index
	global turns

	if raw:
		return
		
	try:
		user = " ".join(message["arguments"][1:])
	
	except IndexError:
		return ["Syntax: smw_kick <user to kick from game>"]
	
	if not user.lower() in user_data.keys():
		return ["He's not joined either!"]
		
	user_data.__delitem__(user.lower())
	
	if turns[turn_index] == user:
		turn_index += 1
		
		if turn_index >= len(turns):
			turn_index = 0
	
	for i, x in enumerate(turns):
		if x == user.lower():
			turns.pop(i)
			
	return ["User kicked succesfully!"]
	
@easy_bot_command("smw_bot_addname")
def add_bot_name(message, raw):
	if raw:
		return
		
	open("botnames.txt", "a").writelines(["\n" + x for x in message["arguments"][1:]])
	return "Names added sucesfully!"
	
@easy_bot_command("smw_togglemush", True)
def toggle_mush(message, raw):
	global user_data

	if raw:
		return
		
	if len(message["arguments"]) < 2:
		return "Syntax: smw_togglemush <number of people to turn into mush>"
		
	user_data = dict({x: dict(user_data[x], mush=not user_data[x]["mush"]) for x in message["arguments"][1:]}, **{x: y for x, y in user_data.items() if x not in message["arguments"][1:]})
	
	return "Toggled users sucesfully!"
	
@bot_command("smw_help")
def smw_help(message, connector, index, raw):
	if raw:
		return
		
	def send_notices(mesgs):
		for item in mesgs:
			connector.send_command(index, "NOTICE {} :{}".format(message["nickname"], item.encode("utf-8")))
		
	connector.send_message(index, get_message_target(connector, message, index), "Sent you help via notice.")

	send_notices((
		"WARZONE HELP",
		"Join using smw_join.",
		"If you are mush, use smw_extract to get more spores (or smw_findspore) and smw_spike to in--I mean \"enlighten\". Or else, buy some good gun using smw_buygun and smw_buyammo. (List them and ammo using smw_listweaponry and smw_listammotypes!)",
		"Use smw_about for etc stuff or use smw_hide for a consolation message!", "Use smw_cost to get cost of stuff. Always remember: friendship is for FREE! <3",
		"Use smw_shoot <target> <weapon> to shoot at someone. Use smw_eat to regain immune/fungushealth. And smw_status to get your status and smw_getstatus to get other people's status!",
		"Some commands are turn-only. Check who's turn using smw_turn and check the turn queue using smw_turns! And check who is playing (and whether they're mush) using smw_players.",
		"Remember: instead of paranoia like in the original, use strategy! ;)"
	))
	
@easy_bot_command("smw_cbm", True)
def condense_them(message, raw):
	global condense_bot_messages

	if raw:
		return
		
	condense_bot_messages = not condense_bot_messages
	return "Now {}condensing bot messages!".format(("not " if not condense_bot_messages else ""))