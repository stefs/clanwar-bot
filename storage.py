# Built-in modules
import collections
import datetime
import logging

# Project modules
import util

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
	('location', Attr('Treffpunkt', util.parse_text, False))])
#	('opponent_homepage', Attr('Homepage des Gegners', util.parse_text, False)),
#	('organizer', Attr('Organisator', util.parse_text, False)),
#	('opponent_contact', Attr('Ansprechpartner des Gegners', util.parse_text, False))])

counter = 0 # debug
class Event:
	def __init__(self):
		global counter
		self.key = counter
		counter += 1
		for attr in event_attr:
			setattr(self, attr, None)

	def __str__(self):
		return '{1} {2} {3}vs{3} gegen {0}'.format(
			self.opponent_tag,
			self.date.strftime('%a. %d. %b'),
			self.time.strftime('%H:%M'),
			self.player_count)

	def summary(self):
		text = list()
		text.append('[{}] {}'.format(self.opponent_tag, self.opponent_name))
#		if self.opponent_homepage:
#			text.append(self.opponent_homepage)
		text.append('{0}vs{0} {1}'.format(self.player_count, self.game_mode))
		text.append('{}, {} Uhr'.format(self.date.strftime('%A %d. %B %Y'), self.time.strftime('%H:%M')))
		if self.location:
			text.append('Treffpunkt: {}'.format(self.location))
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

def get_events():
	return events.values()

def save(event):
	events[event.key] = event

# debug
event = Event()
event.opponent_name = 'Test'
event.opponent_tag = 'TST'
event.date = datetime.date(2004, 4, 1)
event.time = datetime.time(21, 0, 1)
event.game_mode = 'Eroberung'
event.player_count = 3
event.maps = 'Zavod und Shanghai'
event.rules = '42!'
save(event)

