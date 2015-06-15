#!/usr/bin/env python3

# Built-in modules
import logging

# Project modules
import storage
from util import *

# Configure logging
logging.basicConfig(
	format = '[%(asctime)s:%(levelname)s:%(module)s:%(threadName)s] %(message)s',
	datefmt = '%dd%Hh%Mm%Ss',
	level = logging.DEBUG)

# Define states
class State:
	def __init__(self):
		self.next = list()

class Inactive(State):
	def __str__(self):
		return 'Deaktivieren'
	def run(self):
		print('Dies ist der DSO-Clanwar-Bot. Wenn du keine weiteren Nachrichten erhalten willst, brauchst du nichts zu tun. ')
		print('Möchtest du den DSO-Bot nutzen?')
		while not user_input(parse_yesno):
			logging.info('User answered no on opt out')
		current.next.append(Base())

class Base(State):
	def __str__(self):
		return 'Ins Hauptmenü wechseln'
	def run(self):
		print('DSO-Bot hier. Was willst du tun?')
		self.next.append(Schedule())
		self.next.append(ManageEvents())
		self.next.append(ManageUsers())
		self.next.append(Feedback())
		self.next.append(Inactive())

class ManageEvents(State):
	def __str__(self):
		return 'Clanwars verwalten'
	def run(self):
		print('Um welchen Clanwar geht es?')
		self.next.append(NewEvent())
		for event in storage.get_events():
			self.next.append(EditEvent(event))
		current.next.append(Base())

class EditEvent(State):
	def __init__(self, event):
		State.__init__(self)
		self.event = event
	def __str__(self):
		return str(self.event)
	def run(self):
		print(self.event.summary())
		print('Clanwar ändern?')
		for attr in storage.event_attr:
			self.next.append(EditAttr(self.event, attr))
		current.next.append(Base())

class EditAttr(State):
	def __init__(self, event, attr):
		State.__init__(self)
		self.event = event
		self.attr = attr
	def __str__(self):
		return storage.event_attr[self.attr].description
	def run(self):
		attr_details = storage.event_attr[self.attr]
		print('{}?'.format(attr_details.description))
		value = user_input(attr_details.parser)
		setattr(self.event, self.attr, value)
		storage.save(self.event)
		self.next.append(EditEvent(self.event))

class NewEvent(State):
	def __str__(self):
		return 'Neuen Clanwar eintragen'
	def run(self):
		event = storage.Event()
		for attr in storage.event_attr:
			attr_details = storage.event_attr[attr]
			if attr_details.must:
				print('{}?'.format(attr_details.description))
				value = user_input(attr_details.parser)
				setattr(event, attr, value)
		storage.save(event)
		print('Clanwar eingetragen: {}'.format(event))
		current.next.append(Base())

class Schedule(State):
	def __str__(self):
		return 'Zusagen verwalten'
	def run(self):
		print('Funktion leider nicht verfügbar.')
		current.next.append(Base())

class Feedback(State):
	def __str__(self):
		return 'Problem melden'
	def run(self):
		print('Welches Problem gibt es?')
		value = user_input(parse_text)
		# TODO send text
		print('Deine Nachricht wird weitergeleitet.')
		current.next.append(Base())

class ManageUsers(State):
	def __str__(self):
		return 'Benutzer verwalten'
	def run(self):
		print('Funktion leider nicht verfügbar.')
		current.next.append(Base())

# Debug
event = storage.Event()
event.opponent_name = 'Test'
event.opponent_tag = 'TST'
event.date = datetime.date(2004, 4, 1)
event.time = datetime.time(21, 0, 1)
event.game_mode = 'Eroberung'
event.player_count = 3
event.maps = 'Zavod und Shanghai'
event.rules = '42!'
storage.save(event)

# Main loop
current = Inactive()
while True:
	current.run()
	current = multiple_choice(current.next)
