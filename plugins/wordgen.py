import plugincon
import random
import string

vowels = list('aeiou')

def gen_word(min, max):
	word = ''
	syllables = random.randint(min, max)
	for i in range(0, syllables):
		word += gen_syllable()

	return word.capitalize()


def gen_syllable():
	ran = random.random()
	if ran < 0.333:
		return word_part('v') + word_part('c')
	if ran < 0.666:
		return word_part('c') + word_part('v')
	return word_part('c') + word_part('v') + word_part('c')


def word_part(type):
	if type is 'c':
		return random.sample([ch for ch in list(string.lowercase) if ch not in vowels], 1)[0]
	if type is 'v':
		return random.sample(vowels, 1)[0]

@plugincon.easy_bot_command("randomwords")
def random_words(message, raw):
	if raw:
		return

	try:
		number = int(message["arguments"][1])

	except IndexError:
		number = random.randint(15, 30)

	except ValueError:
		if message["arguments"][1] in ("--syntax", "-s", "--help", "-h", "--arguments", "--args", "-a"):
			return "Syntax: randomwords [words] [min. number of syllabes] [max number of syllabes]"

	try:
		min_syllabes = max(int(message["arguments"][2]), 10)

	except IndexError:
		min_syllabes = 2

	try:
		max_syllabes = max(int(message["arguments"][3]), 30)

	except IndexError:
		max_syllabes = random.randint(4, 5)

	return "{}: ".format(message["nickname"]) + " ".join(gen_word(min_syllabes, max_syllabes) for _ in xrange(number))
