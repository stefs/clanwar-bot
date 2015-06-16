# Built-in modules
import string
import logging
import datetime

## Custom application error
class Error(Exception):
	pass

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
	return 'j' in data or 'y' in data

def parse_phone(data):
	data = filter_string(data, string.digits+'+')
	if data:
		return data
	else:
		raise Error('input too short')

def filter_string(data, allowed):
	for char in set(data):
		if char not in allowed:
			data = data.replace(char, '')
	return data

def user_input(parser, read):
	while True:
		try:
			return parser(read())
		except Error as err:
			logging.warning('Parsing failed: {}'.format(err))

def title(title, text):
	if '\n' in text:
		return '{}:\n{}'.format(title, text)
	else:
		return '{}: {}'.format(title, text)
