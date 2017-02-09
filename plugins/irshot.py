# IRShot
# ======================
# A prototype for an 2D topdown (physics) IRC Shooter based on text
#
# by Gustavo R. Rehermann

import plugincon
import random

types = []

class TileType(object):
	def __init__(self, slowdown=1):
		self.slowdown = slowdown
		
	def actor_in(self, other):
		if other.isinstance(Player):
			if other.speed < self.slowdown:
				return False
			
			other.speed -= self.slowdown
			
		return True

class Tile(object):
	def __init__(self, type=0, location=(0,0)):
		self.location = list(location)
		self.type = int(type)

class Actor(object):
	def __init__(self, **kwargs):
		self.properties = kwargs
		
	def touch(self, other):
		pass
		
	def bump(self, other):
		pass
		
class Player(Actor):
	def __init__(self):
		pass
		
	def input(self, line):
		pass