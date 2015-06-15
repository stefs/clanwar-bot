# Built-in modules
import collections
import datetime
import logging

# Project modules
from util import * 

Attr = collections.namedtuple('Attr', ['description', 'parser', 'must'])

event_attr = collections.OrderedDict([
	('opponent_tag', Attr('Clantag des Gegners', parse_text, True)),
	('opponent_name', Attr('Name des Gegners', parse_text, False)),
	('date', Attr('Datum', parse_date, True)),
	('time', Attr('Uhrzeit', parse_time, True)),
	('player_count', Attr('Spielerzahl pro Team', parse_int, True)),
	('game_mode', Attr('Spielmodus', parse_text, True)),
	('maps', Attr('Karten', parse_text, False)),
	('rules', Attr('Regeln', parse_text, False)),
	('location', Attr('Treffpunkt', parse_text, False))])
#	('opponent_homepage', Attr('Homepage des Gegners', parse_text, False)),
#	('organizer', Attr('Organisator', parse_text, False)),
#	('opponent_contact', Attr('Ansprechpartner des Gegners', parse_text, False))])

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
			text.append(title('Karten', self.maps))
		if self.rules:
			text.append(title('Regeln', self.rules))
#		if self.organizer:
#			text.append(title('Organisator', self.organizer))
#		if self.opponent_contact:
#			text.append(title('Ansprechpartner Gegner', self.opponent_contact))
		return '\n'.join(text)

events = dict()

def get_events():
	return events.values()

def save(event):
	logging.debug(event)
	events[event.key] = event
