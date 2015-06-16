#!/usr/bin/env python3

# Set up locale
import locale
locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8')

# Set up logging
import logging
logging.basicConfig(
	format = '[%(asctime)s:%(levelname)s:%(module)s:%(threadName)s] %(message)s',
	datefmt = '%yy%mm%dd%Hh%Mm%Ss',
	level = logging.DEBUG)

# Built-in modules
import traceback

# Project modules
import conversation

# Prepare bot
conversation.send = print
conversation.send_admin = lambda x: print('@admin {}'.format(x))
conversation.receive = input
conversation.my_key = 0

# Start bot
try:
	conversation.start()
except Exception as err:
	tb_lines = traceback.format_tb(err.__traceback__)
	message = '{}: {}\n{}'.format(type(err).__name__, err, ''.join(tb_lines))
	logging.critical(message)
	conversation.send_admin(message)
	conversation.send('Entschuldigung, der Bot ist abgestürtzt und wird nicht '
		'weiter funktionieren. Der Admin wurde informiert.')

