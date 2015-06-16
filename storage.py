# Built-in modules
import collections
import datetime
import logging
import enum

# Project modules
import util

# TODO introduce max edit time for events and members
# TODO use persistent storage
# TODO synchronize with database
# TODO store schedule

Attr = collections.namedtuple('Attr', ['description', 'parser', 'must'])

event_attr = collections.OrderedDict([
	('opponent_tag', Attr('Clantag des Gegners', util.parse_text, True)),
	('opponent_name', Attr('Name des Gegners', util.parse_text, False)),
	('date', Attr('Datum', util.parse_date, True)),
	('time', Attr('Uhrzeit', util.parse_time, True)),
	('player_count', Attr('Spielerzahl pro Team', util.parse_int, True)),
	('game_mode', Attr('Spielmodus', util.parse_text, True)),
	('maps', Attr('Karten', util.parse_text, False)),
	('rules', Attr('Regeln', util.parse_text, False)),
	('location', Attr('Server', util.parse_text, False))])
#	('opponent_homepage', Attr('Homepage des Gegners', util.parse_text, False)),
#	('organizer', Attr('Organisator', util.parse_text, False)),
#	('opponent_contact', Attr('Ansprechpartner des Gegners', util.parse_text, False))])

counter_event = 0 # debug
class Event:
	def __init__(self):
		global counter_event
		self.key = counter_event
		counter_event += 1
		for attr in event_attr:
			setattr(self, attr, None)

	def __str__(self):
		return '{1} {2} {3}vs{3} gegen {0}'.format(
			self.opponent_tag,
			self.date.strftime('%a. %d.%m.'),
			self.time.strftime('%H:%M'),
			self.player_count)

	def summary(self):
		text = list()
		if self.opponent_name:
			text.append('[{}] {}'.format(self.opponent_tag, self.opponent_name))
		else:
			text.append('DSO vs. {}'.format(self.opponent_tag))
#		if self.opponent_homepage:
#			text.append(self.opponent_homepage)
		text.append('{0}vs{0} {1}'.format(self.player_count, self.game_mode))
		text.append('{}, {} Uhr'.format(self.date.strftime('%A %d. %B %Y'), self.time.strftime('%H:%M')))
		if self.location:
			text.append('Server: {}'.format(self.location))
		if self.maps:
			text.append(util.title('Karten', self.maps))
		if self.rules:
			text.append(util.title('Regeln', self.rules))
#		if self.organizer:
#			text.append(util.title('Organisator', self.organizer))
#		if self.opponent_contact:
#			text.append(util.title('Ansprechpartner Gegner', self.opponent_contact))
		return '\n'.join(text)

events = dict()

def save_event(event):
	events[event.key] = event
	logging.info('Event saved: {}'.format(event))

def get_event(key):
	try:
		return events[key]
	except KeyError:
		raise util.Error('event not found')

def set_event_attr(key, attr, value):
	try:
		event = get_event(key)
	except util.Error:
		pass
	else:
		setattr(event, attr, value)
		save_event(event)
		logging.info('{} of {} was updated to {}'.format(attr, event, value))

def get_event_keys():
	return events.keys()

def delete_event(key):
	try:
		del events[key]
	except KeyError:
		pass

event = Event()
event.opponent_tag = 'TST'
event.date = datetime.date(2015, 6, 20)
event.time = datetime.time(20, 30, 0)
event.player_count = 16
event.game_mode = 'Eroberung Klein'
save_event(event)

class Group(enum.Enum):
	leader = 0
	member = 1
	trial = 2

attendance_attr = collections.OrderedDict([
	('default_friday', 'Freitag'),
	('default_saturday', 'Samstag'),
	('default_sunday', 'Sonntag')])

counter_member = 0 # debug
class Member:
	phone_number = None
	psn_name = None
	group = None
	permission = False

	def __init__(self):
		global counter_member
		self.key = counter_member
		counter_member += 1
		for attr in attendance_attr:
			setattr(self, attr, None)

	def __str__(self):
		if self.group is Group.leader:
			return '{}★'.format(self.psn_name)
		elif self.group is Group.trial:
			return '{} (Trial)'.format(self.psn_name)
		else:
			return self.psn_name

	def summary(self):
		text = list()
		text.append('{}, {}'.format(self.psn_name, self.group.name.capitalize()))
		text.append('Telefon: {}'.format(self.phone_number))
		if not self.permission:
			text.append('Hat Erlaubnis für DSO-Bot noch nicht erteilt.')
		return '\n'.join(text)

	def preset_summary(self):
		text = list()
		for attr in attendance_attr:
			text.append('{}: {}'.format(
				attendance_attr[attr],
				attendance_status[getattr(self, attr)]))
		return '\n'.join(text)

members = dict()

def save_member(member):
	members[member.key] = member
	logging.info('Member saved: {}'.format(member))

def get_member(key):
	try:
		return members[key]
	except KeyError:
		raise util.Error('member not found')

def set_member_attr(key, attr, value):
	try:
		member = get_member(key)
	except util.Error:
		pass
	else:
		setattr(member, attr, value)
		save_member(member)
		logging.info('{} of {} was updated to {}'.format(attr, member, value))

def get_member_keys(group):
	members_group = list()
	for key in members:
		if members[key].group is group:
			members_group.append(key)
	return members_group

def delete_member(key):
	try:
		del members[key]
	except KeyError:
		pass

member = Member()
member.phone_number = 234
member.psn_name = 'collin'
member.group = Group(0)
save_member(member)

attendance_status = collections.OrderedDict([
	(0, 'Verbindliche Zusage'),
	(1, 'Unverbindliche Zusage'),
	(2, 'Absage'),
	(None, 'Keine Angabe')])

schedules = dict()

class Schedule:
	member_key = None
	date = None
	event_key = None
	attendance = None

def get_schedule_keys(member_key):
	pass

def compile_schedule(member_key):
	# Get set of relevant dates
	date = datetime.date.today()
	dates = set()
	for number in range(0, 28):
		dates.add(date)
		date += datetime.timedelta(days=1)

	# Get set of events
	events = list()
	for event_key in get_event_keys():
		try:
			events.append(get_event(event_key))
		except util.Error:
			pass

	# Get set of event dates
	event_dates = set()
	for event in events:
		event_dates.add(event.date)

	# Remove event dates from relevant dates
	dates -= event_dates

	# Remove weekdays from relevant dates
	schedule = list()
	for date in dates:
		if date.weekday() >= 4:
			schedule.append((
				datetime.datetime.combine(date, datetime.time(20, 30, 0)),
				None))

	# Add event dates to relevant dates
	for event in events:
		schedule.append((
			datetime.datetime.combine(event.date, event.time),
			event))
	schedule.sort()

	text = list()
	for date_time, event in schedule:
		if event:
			text.append('{}: {}'.format(event, None))
		else:
			text.append('{}: {}'.format(date_time.strftime('%a. %d.%m. %H:%M'),
				None))
	return '\n'.join(text)
