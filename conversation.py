# Built-in modules
import logging
import string

# Project modules
import util
import storage

# Configuration
send = None
send_admin = None
receive = None

# States
class State:
	def __init__(self):
		self.next = list()

class Inactive(State):
	def __str__(self):
		return 'Deaktivieren'
	def run(self):
		send('Dies ist der DSO-Clanwar-Bot. Wenn du keine weiteren Nachrichten erhalten willst, brauchst du nichts zu tun. ')
		send('Möchtest du den DSO-Bot nutzen?')
		while not util.user_input(util.parse_yesno, receive):
			logging.info('User refused opt in')
		self.next.append(Base())

class Base(State):
	def __str__(self):
		return 'Ins Hauptmenü wechseln'
	def run(self):
		send('Hauptmenü DSO-Bot')
		self.next.append(Schedule())
		self.next.append(ManageEvents())
		self.next.append(ManageUsers())
		self.next.append(Feedback())
		self.next.append(Inactive())

class ManageEvents(State):
	def __str__(self):
		return 'Clanwars verwalten'
	def run(self):
		send('Um welchen Clanwar geht es?')
		self.next.append(NewEvent())
		for event in storage.get_events():
			self.next.append(EditEvent(event))
		self.next.append(Base())

class EditEvent(State):
	def __init__(self, event):
		State.__init__(self)
		self.event = event
	def __str__(self):
		return str(self.event)
	def run(self):
		send(self.event.summary())
		send('Clanwar ändern?')
		for attr in storage.event_attr:
			self.next.append(EditAttr(self.event, attr))
		self.next.append(Base())

class EditAttr(State):
	def __init__(self, event, attr):
		State.__init__(self)
		self.event = event
		self.attr = attr
	def __str__(self):
		return storage.event_attr[self.attr].description
	def run(self):
		attr_details = storage.event_attr[self.attr]
		send('{}?'.format(attr_details.description))
		value = util.user_input(attr_details.parser, receive)
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
				send('{}?'.format(attr_details.description))
				value = util.user_input(attr_details.parser, receive)
				setattr(event, attr, value)
		storage.save(event)
		send('Clanwar eingetragen: {}'.format(event))
		self.next.append(Base())

class Schedule(State):
	def __str__(self):
		return 'Zusagen verwalten'
	def run(self):
		send('Funktion leider nicht verfügbar.')
		self.next.append(Base())

class Feedback(State):
	def __str__(self):
		return 'Problem melden'
	def run(self):
		send('Welches Problem gibt es?')
		value = util.user_input(util.parse_text, receive)
		send_admin(value)
		send('Deine Nachricht wurde weitergeleitet.')
		self.next.append(Base())

class ManageUsers(State):
	def __str__(self):
		return 'Benutzer verwalten'
	def run(self):
		send('Funktion leider nicht verfügbar.')
		self.next.append(Base())

# Main loop
def start():
	current = Inactive()
	while True:
		# Run state task
		current.run()

		# Return single option
		if len(current.next) == 1:
			current = current.next[0]
			continue

		# Present options
		choices = dict()
		count = min(len(current.next), len(string.ascii_lowercase))
		for number in range(0, count):
			key = string.ascii_lowercase[number]
			value = current.next[number]
			choices[key] = value
			print('[{}] {}'.format(key, value))

		# Get user choice
		while True:
			key = receive()
			if key in choices:
				current = choices[key]
				break
