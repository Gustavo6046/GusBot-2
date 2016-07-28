from random import randint
from plugincon import bot_command, easy_bot_command, get_message_target, get_bot_nickname, reload_all_plugins

# Tic Tac Toe
ttt_channel_data = {}

@easy_bot_command("tictactoe")
def challenge_to_ttt(message, raw):
	if raw:
		return
		
	if len(message["arguments"]) < 3:
		return ["Error! Syntax: tictactoe <challengee> <(circle|cross)>"]
	
	if message["channel"] in ttt_channel_data.keys() and ttt_channel_data[message["channel"]]["running"]:
		return ["There's already a Tic Tac Toe game in the channel!"]
		
	if message["arguments"][2].lower() not in ("circle", "cross"):
		return ["Error! Choose circle OR cross!"]
		
	elif not message["channel"] in ttt_channel_data.keys():
		ttt_channel_data[message["channel"]] = {}
		ttt_channel_data[message["channel"]]["running"] = True
		ttt_channel_data[message["channel"]]["board"] = {(a, b): None for a in (0, 1, 2) for b in (0, 1, 2)}
		ttt_channel_data[message["channel"]]["inserted"] = 0
		ttt_channel_data[message["channel"]]["challenger"] = message["nickname"].lower()
		ttt_channel_data[message["channel"]]["challengee"] = message["arguments"][1].lower()
		ttt_channel_data[message["channel"]]["accepted"] = False
		ttt_channel_data[message["channel"]]["challengertype"] = message["arguments"][2].lower()
		
	return ["{} is challenging {} to a Tic Tac Toe fight! Use ||ttt_accept or ||ttt_reject !".format(
		message["nickname"],
		message["arguments"][1]
	)]
	
@easy_bot_command("ttt_accept")
def accept_ttt_challenge(message, raw):
	if raw:
		return
		
	if not message["channel"] in ttt_channel_data.keys():
		return ["Error: no challenge to accept!"]
		
	if ttt_channel_data[message["channel"]]["accepted"]:
		return ["Error: Challenge already accepted!"]
		
	ttt_channel_data[message["channel"]]["accepted"] = True
	return ["Challenge Accepted!"]
	
@easy_bot_command("ttt_reject")
def reject_ttt_challenge(message, raw):
	if raw:
		return
		
	if not message["channel"] in ttt_channel_data.keys():
		return ["Error: no challenge to accept!"]
		
	if ttt_channel_data[message["channel"]]["accepted"]:
		return ["Error: Challenge already accepted!"]
		
	ttt_channel_data.__delitem__(message["channel"])
	return ["Challenge Rejected!"]
	
@easy_bot_command("ttt_insert")
def ttt_insert(message, raw):
	if raw:
		return
		
	if not message["channel"] in ttt_channel_data.keys():
		return ["Error: no Tic Tac Toe game running!"]
		
	if not ttt_channel_data[message["channel"]]["accepted"]:
		return ["Error: Challenge not accepted yet!"]
		
	if len(message["arguments"]) < 3:
		return ["Syntax: ttt_insert <x> <y>"]
		
	if message["nickname"].lower() not in (ttt_channel_data[message["channel"]]["challenger"], ttt_channel_data[message["channel"]]["challengee"]):
		return ["Error: You are not playing this channel's game!"]
		
	x = int(message["arguments"][1])
	y = int(message["arguments"][2])
		
	if x > 2 or y > 2 or x < 0 or y < 0:
		return ["Error: Coordinates out of bounds 0-2,0-2!"]
		
	if ttt_channel_data[message["channel"]]["board"][(x, y)]:
		return ["Error: Slot already filled!"]
		
	if message["nickname"] == ttt_channel_data[message["channel"]]["challenger"]:
		ttt_channel_data[message["channel"]]["board"][(x, y)] = ttt_channel_data[message["channel"]]["challengertype"]
		
	else:
		if ttt_channel_data[message["channel"]]["challengertype"] == "circle":
			ttt_channel_data[message["channel"]]["board"][(x, y)] = "cross"
			
		else:
			ttt_channel_data[message["channel"]]["board"][(x, y)] = "circle"
			
	ttt_channel_data[message["channel"]]["inserted"] += 1
	
	return [
		"Inserted at {},{}! Current board:".format(x, y),
		"  0 1 2",
		"0 {}|{}|{}".format(
			str(ttt_channel_data[message["channel"]]["board"][(0, 0)]).replace("circle", "o").replace("cross", "x").replace("None", "."), 
			str(ttt_channel_data[message["channel"]]["board"][(1, 0)]).replace("circle", "o").replace("cross", "x").replace("None", "."),
			str(ttt_channel_data[message["channel"]]["board"][(2, 0)]).replace("circle", "o").replace("cross", "x").replace("None", ".")
		),
		"1 {}|{}|{}".format(
			str(ttt_channel_data[message["channel"]]["board"][(0, 1)]).replace("circle", "o").replace("cross", "x").replace("None", "."), 
			str(ttt_channel_data[message["channel"]]["board"][(1, 1)]).replace("circle", "o").replace("cross", "x").replace("None", "."),
			str(ttt_channel_data[message["channel"]]["board"][(2, 1)]).replace("circle", "o").replace("cross", "x").replace("None", ".")
		),
		"2 {}|{}|{}".format(
			str(ttt_channel_data[message["channel"]]["board"][(0, 2)]).replace("circle", "o").replace("cross", "x").replace("None", "."),
			str(ttt_channel_data[message["channel"]]["board"][(1, 2)]).replace("circle", "o").replace("cross", "x").replace("None", "."),
			str(ttt_channel_data[message["channel"]]["board"][(2, 2)]).replace("circle", "o").replace("cross", "x").replace("None", ".")
		)
	]
	
# Thievery

thf_user_data = {}

def sort_board(coordinate_light):
	return coordinate_light[0][0] + 1 * coordinate_light[0][1] + 1

def player_at(nick, x, y):
	return (x, y) == thf_user_data[nick]["player_at"]
	
def lightning_char(value, nick, x, y):
	if player_at(nick, x, y):
		return "Oz"

	if value < 10:
		return "+"
		
	if value < 40:
		return "-"
	
	if value < 60:
		return ","
	
	if value < 80:
		return "."
	
	return "\'"
	
def render_board(board, nick):
	print "Sorting board..."
	board_sorted = sorted(board.items(), key=sort_board)
	
	board_list = [""]
	
	print "Started rendering!"
	
	for cl in board_sorted:
		while cl[0][1] >= len(board_list):
			board_list.append("")
				
		print "Stage 1 done!"
				
		while cl[0][0] >= len(board_list[cl[0][1]]):
			board_list[cl[0][1]] += " "
		
		print "Stage 2 done!"
			
		board_list[cl[0][1]] = board_list[cl[0][1]][:cl[0][0] - 1] + lightning_char(cl[1], nick, cl[0][0], cl[0][1]) + board_list[cl[0][1]][cl[0][0] - 1:]
	
	return board_list
	
def starting_board():
	width = randint(10, 60)
	height = randint(10, 18)
	
	return [{(x, y): randint(0, 100) for x in xrange(width) for y in xrange(height)}, [width, height]]

@easy_bot_command("thief_stop")
def thievery_end_game(message, raw):
	if raw:
		return
		
	if message["nickname"] not in thf_user_data.keys():
		return ["You don't have a game running!"]
		
	thf_user_data.__delitem__[message["nickname"]]
	
	return ["Game ended."]
	
@easy_bot_command("thief_start")
def thievery_start_game(message, raw):
	if raw:
		return
		
	if message["nickname"] in thf_user_data.keys():
		return ["Already started your game!"]
		
	stb = starting_board()
		
	thf_user_data[message["nickname"]] = {
		"board": stb[0],
		"size": stb[1],
		"player_at": [randint(0, stb[1][0]), randint(0, stb[1][1])]
	}
		
	return ["Game started! Board:", " "] + render_board(thf_user_data[message["nickname"]]["board"], message["nickname"])
	
def clamp(value, rangemin, rangemax):
	if value < rangemin:
		return rangemin
	
	if value > rangemax:
		return rangemax
		
	return value
	
@easy_bot_command("thief_move")
def thievery_move(message, raw):
	if raw:
		return
	
	if message["nickname"] not in thf_user_data.keys():
		return ["Start a game first!"]
	
	if len(message["arguments"]) < 3:
		return ["Syntax: thief_move <move_x> <move_y>", "Both move_x and move_y must be smaller than 2 and greater than -2."]
	
	x = clamp(message["arguments"][1], -1, 1)
	y = clamp(message["arguments"][2], -1, 1)
	
	thf_user_data[message["nickname"]]["player_at"][0] += x
	thf_user_data[message["nickname"]]["player_at"][1] += y
	
	return ["Moved succesfully! New board:", " "] + render_board(thf_user_data[message["nickname"]]["board"], message["nickname"])