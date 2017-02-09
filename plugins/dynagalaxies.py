__doc__ = """
Dynagalaxies
__________________

Generate a small virtual universe and create a galactical empire on it!
All in a 3D universe for fun hours of playtime!

(c) 2016 Gustavo Ramos "Gustavo6046" Rehermann, MIT License source-code | CC-BY 3.0 otherwise
"""

import random
import plugincon
import math
import time
import threading
import re

actor_classes = set()
actors = {}
players = {}
turn_index = 0

def turnlist():
	return sorted([x for x, y in players.items()], key=lambda x: players[x].index)

class Vector(object):
	def __init__(self, x, y, z):
		self.x = x
		self.y = y
		self.z = z
	
	def __add__(self, other):
		self.x += other.x
		self.y += other.y
		self.z += other.z
		
		return self
	
	def __sub__(self, other):
		self.x -= other.x
		self.y -= other.y
		self.z -= other.z
		
		return self
		
	def __mul__(self, other):
		if isinstance(other, Vector):
			self.x *= other.x
			self.y *= other.y
			self.z *= other.z
			
		self.x *= other
		self.y *= other
		self.z *= other
		
		return self
	
	def __div__(self, other):
		if isinstance(other, Vector):
			self.x /= other.x
			self.y /= other.y
			self.z /= other.z
		
		self.x /= other
		self.y /= other
		self.z /= other
		
		return self
		
	def __len__(self, squared=False):
		result = abs(self.x**2 + self.y**2 + self.z**2)
	
		if not squared:
			return math.sqrt(result)
			
		return result
	
	def normal(self):
		result = Vector(self.x, self.y, self.z)
		
		biggest_axis = sorted([result.x, result.y, result.z])[-1]
		
		result /= biggest_axis
		return result
		
class BoundingBox(object):
	def __init__(self, a=Vector(0, 0, 0), b=Vector(0, 0, 0)):
		if not (isinstance(a, Vector) or isinstance(b, Vector)):
			print "Warning: Caught try to instantiate BoundingBox with invalid bounding vector values! Setting both to 0,0,0."
			self.a = Vector(0, 0, 0)
			self.b = Vector(0, 0, 0)
			
		self.a = a
		self.b = b
		
	def check_collision(self, vect):
		if isinstance(vect, Vector):
			return (vect.x > self.a.x and vect.x < self.b.x
				and vect.y > self.a.y and vect.y < self.b.y
				and vect.z > self.a.z and vect.z < self.b.z)
				
		elif isinstance(vect, BoundingBox):
			vec = vect.a
			vc2 = vect.b
			return (vec.x > self.a.x and vec.x < self.b.x
				and vec.y > self.a.y and vec.y < self.b.y
				and vec.z > self.a.z and vec.z < self.b.z
				
				and vc2.x > self.a.x and vc2.x < self.b.x
				and vc2.y > self.a.y and vc2.y < self.b.y
				and vc2.z > self.a.z and vc2.z < self.b.z)
				
		else:
			return False
		
class GameObject(object):
	def __init__(self, location, bb=BoundingBox(Vector(0, 0, 0), Vector(0, 0, 0))):
		self.location = location
		self.bb = bb
		
	def move_by_vector(self, x, y, z):
		self.x += x
		self.y += y
		self.z += z
		
def actor_iterator(func):
	def wrapper(*args):
		return [actor for actor in actors if func(actor, *args)]
		
class GameActor(GameObject):
	def __init__(self, location, bb=BoundingBox(Vector(0, 0, 0), Vector(0, 0, 0)), props={}):
		actor_classes.add(self.__class__)
	
		super(GameActor, self).__init__(location, bb)
	
		try:
			actors[self.__class__.__name__].append(self)
			
		except KeyError:
			actors[self.__class__.__name__] = [self]
		
		self.turned = False
		
		self.properties = props
		self.initialize()
		
	def get_closer_actor(self, kind, start=0, end=None):
		if end == None:
			return filter(lambda x: x.__class__ == kind, sorted([item for sublist in actors.values() for item in sublist], key=lambda x: len(x.location - self.location)))[start]

		return filter(lambda x: x.__class__ == kind, sorted([item for sublist in actors.values() for item in sublist], key=lambda x: len(x.location - self.location)))[start:end]
		
	def initialize(self):
		pass
		
	def turn_check(func):
		def wrapper(self):
			if not self.turned:
				func()
				self.turned = True
		
	@turn_check
	def turn(self):
		pass
		
class Building(GameActor):
	def create_actor(actor, player):
		pass
		
class Hangar(Building):
	pass

class Town(Building):
	pass
	
class Unit(GameActor):
	pass
	
class Extractor(Unit):
	pass
	
class Explorer(Unit):
	pass
	
class Builder(Unit):
	pass
	
class Starship(Unit):
	pass
		
class MassActor(GameActor):
	def initialize(self):
		try:
			self.velocity = self.properties["velocity"]
			
		except KeyError:
			self.velocity = Vector(0, 0, 0)
			
		self.real_initialize()
			
	def turn(self):
		self.location += self.velocity
		self.velocity += self.turn_velocity()
		
		for actor in [actor for actor in actors if issubclass(actor.__class__, MassActor)]:
			if actor.bb.check_collision(self.bb):
				self.touch(actor)
		
		self.real_turn()
		
	def turn_velocity(self):
		return Vector(0, 0, 0)
		
	def real_turn(self):
		pass
	
class Player(object):
	def __init__(self, name):
		self.name = name
		self.index = len(players.keys())
		self.health = 100
		self.codename = name.lower()
		self.resources = {}
		
		players[self.codename] = self
		
	def take_damage(self, damage):
		self.health -= damage
		
		if self.health <= 0:
			self.die()
			return True
			
		return False
			
	def die(self):
		del players["codename"]
		
class Starship(MassActor):
	def initialize():
		self.planet = get_closer_actor(self.location, Planet)
		self.speed = self.properties["speed"]
		self.contents = {}

	def go_to(planet):
		self.velocity += (self.planet.location - self.location).normal() * self.speed
		
class Planet(MassActor):
	def real_initialize(self):
		self.oxygen = random.randint(0, 100)
		self.iron = random.randint(50, 800)
		self.mass = self.properties["mass"]
		
		self.star = self.properties["star"]
		
		self.known_oxygen = 0
		self.known_iron = 0
		
		self.building_types = {
			"hangar": Hangar,
			"town": Town,
		}
		
		self.unit_types = {
			"starship": (Starship, "Hangar", {"iron": 20}),
			"builder": (Builder, "Town", {"oxygen": 15}),
			"explorer": (Explorer, "Town", {"oxygen": 8}),
			"extractor": (Extractor, "Hangar", {"iron": 6, "oxygen": 9}),
			"extracter": (Extractor, "Hangar", {"iron": 6, "oxygen": 9}),
		}
		
		self.owner = None
		self.units = {}
		self.buildings = {}
		
	@classmethod
	def action_types(cls):
		return {"create_unit", "explore", "extract", "build", "get_coords", "closer_planets"}
		
	def input(self, action, arguments, player):
		if action == "closer_planets":
			return ["List of close planets |->| "] + [planet_info_template.format(x=a.location.x, y=a.location.y, z=a.location.z, distance=len(a.location - self.location), index=actors["Planet"].index(a)) for a in self.get_closer_actor(Planet, 0, 5)]
	
		if action == "get_coords":
			return "Coordinates: {},{},{}".format(*self.location)
	
		if self.owner != player.codename:
			return "Error: You do not own this planet!"
	
		if action == "explore":
			if not "Explorer" in self.units.keys() or self.units["Explorer"] <= 0:
				return
				
			self.units["explorer"].pop(-1)
			
			self.known_oxygen += random.randint(0, 74)
			self.known_iron += random.randint(0, 74)
			
			if self.known_oxygen > self.oxygen:
				self.known_oxygen = self.oxygen
			
			if self.known_iron > self.iron:
				self.known_iron = self.iron
			
			return
		
		if action == "build":
			if not "Builder" in self.units.keys() or self.units["Builder"] <= 0:
				return
				
			self.units["builder"].pop(-1)

			try:
				if arguments[0].lower() in self.buildings.keys():
					self.buildings[arguments[0].lower()].append(self.buildings_types[arguments[0].lower()]())
				
				else:
					self.buildings[arguments[0].lower()] = [self.buildings_types[arguments[0].lower()]()]
			
			except IndexError:
				return "Error: Use the building name as an argument! Building types accepted: " + ", ".join(self.building_types.keys())
				
			except KeyError:
				return "Error: No such building type! Valid types: " + ", ".join(self.building_types.keys())
			
			return "Success building {}!".format(arguments[0].lower())
			
		if action == "create_unit":
			try:
				unit_type = self.unit_types[arguments[0].lower()]
		
			except IndexError:
				return "Error: Provide the kind of unit in one of the arguments!"
				
			except KeyError:
				return "Error: No such unit kind! Unit types available: " + ", ".join(set([x[0].__name__ for x in self.unit_types.values()]))
		
			if unit_type[1].lower() not in self.buildings.keys():
				return "Error: No {} to create {}!".format(unit_type[1].lower(), arguments[0].lower())
		
			for resource, cost in unit_type[2]:
				if resource.lower() not in player.resources.keys() or player.resources[resource.lower()] < cost:
					return "Error: Not enough {}! (you need {}, you have {})".format(resource, cost, player.resources[resource.lower()])
		
			for i in xrange(len(self.buildings[unit_type[1].lower()])):
				try:
					self.units[unit_type[0].__name__].append(unit_type[0]())
			
				except KeyError:
					self.units[unit_type[0].__name__] = [unit_type[0]()]
				
			return "Unit created sucesfully!"
			
		if action == "extract":
			if "extractor" not in self.units.keys() or self.units["extractor"] == []:
				return "Error: No Extractor unit to perform the extraction of iron and oxygen!"
				
			if self.known_oxygen <= 0 or self.known_iron <= 0:
				return "Error: Not enough oxygen/iron found! Explore to see if there's still more in this planet!"
				
			extracted_iron = 0
			extracted_oxygen = 0
				
			for i in xrange(len(self.units["extractor"])):
				extracted_oxygen += random.randint(5, 80)
				extracted_iron += random.randint(10, 90)
			
			if extracted_iron > self.known_iron:
				extracted_iron = self.known_iron
				
			if extracted_oxygen > self.known_oxygen:
				extracted_oxygen = self.known_oxygen
				
			self.iron -= extracted_iron
			self.known_iron -= extracted_iron
			self.oxygen -= extracted_oxygen
			self.known_oxygen -= extracted_oxygen
			
			if "iron" not in player.resources.keys():
				player.resources["iron"] = extracted_iron
			
			else:
				player.resources["iron"] += extracted_iron
				
			if "oxygen" not in player.resources.keys():
				player.resources["oxygen"] = extracted_oxygen
			
			else:
				player.resources["oxygen"] += extracted_oxygen
			
			return "Success extracting iron and oxygen! Extracted {} and {} from the mines of the planet!"
		
	def turn_velocity(self):
		result = Vector(0, 0, 0)
	
		for type in [y for x, y in actors.items() if x in ("Planet", "Star")]:
			for actor in type:
				result += (actor.location - self.location) * actor.properties["mass"] * self.properties["mass"]
			
		return result
		
class Star(GameActor):
	def initialize(self):
		for i in xrange(random.randint(0, 15)):
			mass = random.randint(5, 35) * 0.1
			loct = Vector(random.randint(-16, 16), random.randint(-16, 16), random.randint(-16, 16))
			
			Planet(self.location + loct, BoundingBox(Vector(-mass, -mass, -mass) + loct, Vector(mass, mass, mass) + loct), {"velocity": Vector(random.randint(-24, 24), random.randint(-24, 24), random.randint(-24, 24)), "star": self, "mass": mass})
		
class Galaxy(GameActor):
	def initialize(self):
		for i in xrange(random.randint(40, 120)):
			Star(self.location + Vector(random.randint(-256, 256), random.randint(-256, 256), random.randint(-256, 256)), BoundingBox(), {"mass": random.randint(8, 150) * 0.1, "owner": None})

for i in xrange(random.randint(5, 15)):
	Galaxy(Vector(random.randint(-1024, 1024), random.randint(-1024, 1024), random.randint(-1024, 1024)))
		
num_actors = 0
	
for x in actors.values():
	num_actors += len(x)
	
print "Number of actors: " + str(num_actors)
print "Number of planets: " + str(len(actors["Planet"]))

def advance_turn():
	for x in actors.values():
		for y in x:
			y.turn()
			
	turn_index += 1
	
	if turn_index >= len(turnlist()):
		turn_index = 0
			
def is_turn(user):
	return turnlist()[turn_index] == user.lower()
	
def get_turn():
	return turnlist()[turn_index]
	
def turn_counter(user):
	if not len(players.keys()):
		return

	time.sleep(30)
	
	if get_turn().lower() == user.lower():
		advance_turn()
	
@plugincon.easy_bot_command("dg_action")
def action(message, raw):
	if raw:
		return
	
	try:
		subject = message["body"].split(";")[0].strip()
		index = message["body"].split(";")[1].strip()
		action = message["body"].split(";")[2].strip()
		aa = [x.strip() for x in ";".join(message["body"].split(";")[3:]).split(",")]
		
	except IndexError:
		return "Syntax (semicolon-separated): dg_action <action subject's kind or *>; <action subject's index or * (does not matter if the subject's kind is \"*\")>; <action name>; [<comma-separated action arguments | semicolons ignored here>]"
	
	try:
		players[message["nickname"].lower()]
		
	except KeyError:
		return "You need to join before using this!"
	
	if subject == "*":
		for kinda in actors.values():
			if index == "*":
				for actor in kinda:
					try:
						action_messages.append(actor.input(action, aa, players[message["nickname"].lower()]))
						
					except AttributeError:
						break
					
			else:
				try:
					action_messages.append(kinda[int(index)].input(action, aa, players[message["nickname"].lower()]))
					
				except ValueError:
					return "Error: Invalid int literal for index ({})!".format(index)
					
				except IndexError:
					action_messages.append(kinda[-1].input(action, aa, players[message["nickname"].lower()]))
					
				except AttributeError:
					continue
					
		return
					
	action_messages = []
					
	try:
		if index == "*":
			for i, actor in enumerate(actors[subject]):
				result = actor.input(action, aa, players[message["nickname"].lower()])
				
				if not isinstance(result, str) and hasattr(result, "__iter__"):
					for x in ["\x02\x035<{} {}>\x0f"] + result:
						action_messages.append(x)
						
					continue
				
				action_messages.append("\x02\x035<{} {}>\x0f".format(actor.__class__.__name__, i) + result)
				
		else:
			try:
				action_messages.append(actors[subject][int(index)].input(action, aa, players[message["nickname"].lower()]))
			
			except ValueError:
				return "Error: Invalid int literal for index ({})!".format(index)
				
			except IndexError:
				return "Error: Actor {} not in {} list!".format(index, subject)
	
	except KeyError:
		raise
		return "Error: No such kind ({}) or no such actor of such kind!".format(subject)
		
	except AttributeError:
		raise
		return "Error: Kind {} does not accept input!".format(subject)
		
	x = filter(lambda x: x, action_messages)
	
	if len(x) > 9:
		y = len(x)
		x = x[:9]
		return x + ["...and {} more messages!".format(y - len(x))]
		
	return x
	
planet_info_template = "Planet Index {index} in Planepedia || Distance: {distance} | Coordinates: X={x};Y={y};Z={z}"
	
@plugincon.easy_bot_command("dg_actiontypes")
def get_action_types(message, raw):
	if raw:
		return
		
	action_types = {}
	
	for classy in actor_classes:
		if hasattr(classy, "action_types"):
			try:
				action_types[classy.__name__] += filter(lambda x: x not in action_types[classy.__name__], tuple(classy.action_types()))
				
			except KeyError:
				action_types[classy.__name__] = list([classy.action_types()])
				
	action_types = {x: tuple(y)[0] for x, y in action_types.items()}
				
	print action_types
	return "Action types: " + "; ".join([": ".join([x, ", ".join(y)]) for x, y in action_types.items()])
	
@plugincon.easy_bot_command("dg_countactors")
def count_actors(message, raw):
	if raw:
		return

	num_actors = 0
		
	for x in actors.values():
		num_actors += len(x)

	return ["Number of actors: " + str(num_actors), "Number of planets: " + str(len(actors["Planet"]))]
	
@plugincon.easy_bot_command("dg_turn")
def get_turn_command(message, raw):
	if raw:
		return

	if not len(players.keys()):
		return "It's nobody's turn! No one's playing!"
	
	return "It's now {}'s turn!".format(get_turn())
	
@plugincon.easy_bot_command("dg_join")
def join_dynagalaxies(message, raw):
	if raw:
		return
	
	user = message["nickname"].lower()
	
	if user in players.keys():	
		return "You already joined! To quit, use dg_quit."
	
	newplayer = Player(message["nickname"])
	
	random.choice(actors["Planet"]).owner = newplayer
	
	return "Joined succesfully!"	

@plugincon.easy_bot_command("dg_endturn")
def end_turn(message, raw):
	if raw:
		return

	advance_turn()
	
	return "It's now {}'s turn!".format(get_turn())
	
@plugincon.easy_bot_command("dg_quit")
def quit_dynagalaxies(message, raw):
	if raw:
		return

	if get_turn() == message["nickname"].lower():
		advance_turn()

	del players[message["nickname"].lower()]
	
	return "Quit-- er, suicide successful! ^_^"