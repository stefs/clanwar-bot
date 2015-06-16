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
my_key = None

# States
class State:
	def __init__(self):
		self.next = list()

class Initial(State):
	def __str__(self):
		return 'Bot neustarten'
	def run(self):
		if not storage.get_member(my_key).permission:
			send('Hallo, dies ist der DSO-Bot. Möchtest du ihn '
				'nutzen um Zusagen zu Clanwars zu verwalten?')
			if util.user_input(util.parse_yesno, receive):
				storage.set_member_attr(my_key, 'permission', True)
			else:
				self.next.append(OptOut())

class OptOut(State):
	def __str__(self):
		return 'Deaktivieren'
	def run(self):
		storage.set_member_attr(my_key, 'permission', False)
		send('Du wirst keine Nachrichten mehr erhalten. '
			'Um den DSO-Bot wieder zu aktivieren, '
			'antworte mit "ja".')
		while not util.user_input(util.parse_yesno, receive):
			pass
		self.next.append(Initial())

class Base(State):
	def __str__(self):
		return 'Ins Hauptmenü wechseln'
	def run(self):
		send('Hallo {}!'.format(storage.get_member(my_key)))
		self.next.append(ManageSchedule())
		self.next.append(SchedulePresets())
		self.next.append(ManageEvents())
		self.next.append(ManageMembers())
		self.next.append(Feedback())
		self.next.append(OptOut())

class ManageEvents(State):
	def __str__(self):
		return 'Clanwars verwalten'
	def run(self):
		event_keys = storage.get_event_keys()
		if event_keys:
			send('Um welchen Clanwar geht es?')
			self.next.append(NewEvent())
			for event_key in event_keys:
				self.next.append(EditEvent(event_key))
			self.next.append(Base())
		else:
			send('Kein Clanwar eingetragen') # TODO test

class EditEvent(State):
	def __init__(self, event_key):
		State.__init__(self)
		self.event_key = event_key
	def __str__(self):
		return str(storage.get_event(self.event_key))
	def run(self):
		event = storage.get_event(self.event_key)
		send(event.summary())
		send('Clanwar ändern?')
		for attr in storage.event_attr:
			self.next.append(EditEventAttr(self.event_key, attr))
		self.next.append(DeleteEvent(self.event_key))
		self.next.append(Base())

class DeleteEvent(State):
	def __init__(self, event_key):
		State.__init__(self)
		self.event_key = event_key
	def __str__(self):
		return 'Clanwar absagen'
	def run(self):
		event = storage.get_event(self.event_key)
		send('Clanwar am {} wirklich absagen und löschen?'.format(event))
		if util.user_input(util.parse_yesno, receive):
			storage.delete_event(self.event_key)
			send('Clanwar abgesagt.')
		else:
			self.next.append(EditEvent(self.event_key))

class EditEventAttr(State):
	def __init__(self, event_key, attr):
		State.__init__(self)
		self.event_key = event_key
		self.attr = attr
	def __str__(self):
		return storage.event_attr[self.attr].description
	def run(self):
		attr_details = storage.event_attr[self.attr]
		send('{}?'.format(attr_details.description))
		value = util.user_input(attr_details.parser, receive)
		storage.set_event_attr(self.event_key, self.attr, value)
		self.next.append(EditEvent(self.event_key))

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
		storage.save_event(event)
		send('Clanwar gespeichert.')
		self.next.append(EditEvent(event.key))

class Feedback(State):
	def __str__(self):
		return 'Problem melden'
	def run(self):
		send('Welches Problem gibt es?')
		value = util.user_input(util.parse_text, receive)
		send_admin(value)
		send('Deine Nachricht wurde weitergeleitet.')

class ManageMembers(State):
	def __str__(self):
		return 'Mitglieder verwalten'
	def run(self):
		send('Was willst du tun?')
		self.next.append(NewMember())
		for group in storage.Group:
			self.next.append(EditMemberChoose(group))
		self.next.append(Base())

class NewMember(State):
	def __str__(self):
		return 'Neues Mitglied hinzufügen'
	def run(self):
		send('Bitte füge nur Personen hinzu, die ausdrücklich zugestimmt'
			'haben den DSO-Bot zu nutzen. Fortfahren?')
		if not util.user_input(util.parse_yesno, receive):
			self.next.append(ManageMembers())
			return
		member = storage.Member()
		send('WhatsApp-Nummer?')
		member.phone_number = util.user_input(util.parse_phone, receive)
		send('PSN-Name?')
		member.psn_name = util.user_input(util.parse_text, receive)
		storage.save_member(member)
		send('Team-Status?')
		for group in storage.Group:
			self.next.append(EditMemberGroup(member.key, group))

class EditMemberChoose(State):
	def __init__(self, group):
		State.__init__(self)
		self.group = group
	def __str__(self):
		return 'Einen {} bearbeiten'.format(self.group.name.capitalize())
	def run(self):
		member_keys = storage.get_member_keys(self.group)
		if member_keys:
			send('Welchen {} bearbeiten?'.format(self.group.name.capitalize()))
			for member_key in member_keys: # TODO too much
				self.next.append(EditMember(member_key))
			self.next.append(ManageMembers())
			self.next.append(Base())
		else:
			send('Kein {} eingetragen'.format(self.group.name.capitalize()))
			self.next.append(ManageMembers())

class EditMember(State):
	def __init__(self, member_key):
		State.__init__(self)
		self.member_key = member_key
	def __str__(self):
		return str(storage.get_member(self.member_key))
	def run(self):
		member = storage.get_member(self.member_key)
		send(member.summary())
		self.next.append(EditMemberPhone(self.member_key))
		self.next.append(EditMemberPSN(self.member_key))
		for group in storage.Group:
			self.next.append(EditMemberGroup(self.member_key, group))
		self.next.append(DeleteMember(self.member_key))
		self.next.append(NewMember())
		self.next.append(ManageMembers())
		self.next.append(Base())

class DeleteMember(State):
	def __init__(self, member_key):
		State.__init__(self)
		self.member_key = member_key
	def __str__(self):
		return 'Mitglied löschen'
	def run(self):
		member = storage.get_member(self.member_key)
		send('{} wirklich löschen?'.format(member))
		if util.user_input(util.parse_yesno, receive):
			storage.delete_member(self.member_key)
			send('{} wurde gelöscht.'.format(member))
			self.next.append(ManageMembers())
		else:
			self.next.append(EditMember(self.member_key))

class EditMemberPhone(State):
	def __init__(self, member_key):
		State.__init__(self)
		self.member_key = member_key
	def __str__(self):
		return 'Telefonnummer bearbeiten'
	def run(self):
		send('WhatsApp-Nummer?')
		value = util.user_input(util.parse_phone, receive)
		storage.set_member_attr(self.member_key, 'phone_number', value)
		self.next.append(EditMember(self.member_key))

class EditMemberPSN(State):
	def __init__(self, member_key):
		State.__init__(self)
		self.member_key = member_key
	def __str__(self):
		return 'PSN-Name bearbeiten'
	def run(self):
		send('PSN-Name?')
		value = util.user_input(util.parse_text, receive)
		storage.set_member_attr(self.member_key, 'psn_name', value)
		self.next.append(EditMember(self.member_key))

class EditMemberGroup(State):
	def __init__(self, member_key, group):
		State.__init__(self)
		self.member_key = member_key
		self.group = group
	def __str__(self):
		return 'Zum {} machen'.format(self.group.name.capitalize())
	def run(self):
		storage.set_member_attr(self.member_key, 'group', self.group)
		self.next.append(EditMember(self.member_key))

class SchedulePresets(State):
	def __str__(self):
		return 'Voreinstellung für Zusagen'
	def run(self):
		me = storage.get_member(my_key)
		if not me:
			error('failed to get self from database')
			return
		send('Voreinstellungen für neue Clanwars nach Wochentagen:\n{}'.format(
			me.preset_summary()))
		for attr in storage.attendance_attr:
			self.next.append(SchedulePresetsChoose(me, attr))
		self.next.append(Base())

class SchedulePresetsChoose(State):
	def __init__(self, me, attr):
		State.__init__(self)
		self.me = me
		self.attr = attr
	def __str__(self):
		return '{} ändern'.format(storage.attendance_attr[self.attr])
	def run(self):
		send('Voreinstellung für neue Clanwars an {}en?'.format(
			storage.attendance_attr[self.attr]))
		self.next.append(EditSchedulePreset(self.me, self.attr, 1))
		self.next.append(EditSchedulePreset(self.me, self.attr, 2))
		self.next.append(EditSchedulePreset(self.me, self.attr, None))

class EditSchedulePreset(State):
	def __init__(self, me, attr, status):
		State.__init__(self)
		self.me = me
		self.attr = attr
		self.status = status
	def __str__(self):
		return storage.attendance_status[self.status]
	def run(self):
		setattr(self.me, self.attr, self.status)
		storage.save_member(self.me)
		self.next.append(SchedulePresets())

class ManageSchedule(State):
	def __str__(self):
		return 'Zusagen verwalten'
	def run(self):
		send('Funktion nicht verfügbar')

# Main loop
def start():
	current = Initial()
	while True:
		# Log status
		logging.info('User status: {}'.format(type(current).__name__))
	
		# Run state task
		current.run()
		
		# Return to menu on missing options
		if not current.next:
			current = Base()
			continue

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
			if key == '0':
				current = Base()
				break
			elif key in choices:
				current = choices[key]
				break

def error(problem):
	send('Entschuldigung, es ist ein Fehler aufgetreten. Der Admin wurde informiert.')
	send_admin(problem)
