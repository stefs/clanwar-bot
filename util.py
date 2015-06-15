# Built-in modules
import string
import logging
import datetime

## Custom application error
class Error(Exception):
	pass

## Get user choice
#  @param options List of objects, presented with str method
#  return Choosen object
def multiple_choice(options):
	# Return single option
	if len(options) == 1:
		return options[0]

	# Cap options length
	options = options[:len(string.ascii_lowercase)]
	
	# Present options
	choices = dict()
	for number in range(0, len(options)):
		key = string.ascii_lowercase[number]
		value = options[number]
		choices[key] = value
		print('[{}] {}'.format(key, value))

	# Get user choice
	while True:
		key = input()
		if key in choices:
			return choices[key]

def parse_text(data):
	return data[:128]

# Parse a date of format 'd.m'
def parse_date(data):
	# Parse day and month
	data_list = data.split('.')
	if len(data_list) < 2:
		raise Error('missing dots')
	day = filter_string(data_list[0], string.digits)
	day = parse_int(day)
	month = filter_string(data_list[1], string.digits)
	month = parse_int(month)

	# Move date with past month in next year
	year = datetime.date.today().year
	if month < datetime.date.today().month:
		year += 1

	# Create date object
	try:
		return datetime.date(year, month, day)
	except ValueError as err:
		raise Error(err)

# Parse a time of format 'hmm'
def parse_time(data):
	data = filter_string(data, string.digits)
	if len(data) < 3:
		raise Error('input too short')
	hour = int(data[-4:-2])
	minute = int(data[-2:])
	try:
		return datetime.time(hour, minute)
	except ValueError as err:
		raise Error(err)

def parse_int(data):
	try:
		return(int(data))
	except ValueError as err:
		raise Error(err)

def parse_yesno(data):
	data = filter_string(data, string.ascii_letters).lower()
	return data in ['ja', 'yes']

def filter_string(data, allowed):
	for char in set(data):
		if char not in allowed:
			data = data.replace(char, '')
	return data

def user_input(parser):
	while True:
		try:
			return parser(input())
		except Error as err:
			logging.warning(err)

def quote(text):
	text = text.split('\n')
	out = list()
	for line in text:
		out.append('| {}'.format(line))
	return '\n'.join(out)

def title(title, text):
	if '\n' in text:
		return '{}:\n{}'.format(title, text)
	else:
		return '{}: {}'.format(title, text)
