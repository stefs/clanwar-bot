#!/usr/bin/env python3

# Set up logging
import logging
logging.basicConfig(
	format = '[%(asctime)s:%(levelname)s:%(module)s:%(threadName)s] %(message)s',
	datefmt = '%yy%mm%dd%Hh%Mm%Ss',
	level = logging.DEBUG)

# Project modules
import conversation

# Prepare bot
conversation.send = print
conversation.send_admin = lambda x: print('@admin {}'.format(x))
conversation.receive = input

# Start bot
conversation.start()

