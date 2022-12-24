#!/usr/bin/env python

from db import Database
import json
import os
import telegram
from telegram import ParseMode
from telegram.ext import Filters, MessageHandler, Updater
import telegram.utils.helpers

DEF_PREVIEW_LEN = 100

with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "config_private.json")) as file:
	config = json.load(file)

class SinglishTranslator:
	def __init__(self, terms):
		self.term_tree = {}

		for term in terms:
			tree = self.term_tree

			for char in term.lower():
				if char.lower() not in tree:
					tree[char] = {}

				tree = tree[char]

			tree[None] = term

	def find_singlish(self, text):
		text = text.lower()

		result = []

		for i in range(len(text)):
			tree = self.term_tree

			match = None

			for j in range(i, len(text)):
				if text[j] not in tree:
					break

				tree = tree[text[j]]

				if None in tree:
					match = tree[None]

			if match is not None:
				result.append(match)

		return result

	def singlish_starting_with(self, prefix):
		tree = self.term_tree

		for char in prefix.lower():
			if char not in tree:
				return set()

			tree = tree[char]

		result = set()

		def dfs(tree):
			for key, value in tree.items():
				if key is None:
					result.add(value)
				else:
					dfs(value)

		dfs(tree)

		return result

translator = SinglishTranslator(Database().terms())

def command_handler(update, context):
	args = update.message.text.split()

	if args[0].startswith("/definition"):
		term = " ".join(args[1:])

		response = term_definition(term, Database())

		if response is None:
			segments = ["I'm sorry; I don't recognize that term\\."]

			if len(singlish := translator.singlish_starting_with(term)) > 0:
				segments.append(" Did you mean:")

				for term in singlish:
					segments.append(
						f"\n`/definition {telegram.utils.helpers.escape_markdown(term, version=2)}`"
					)

			response = "".join(segments)
	elif args[0].startswith("/help") or args[0].startswith("/start"):
		response = """\
Hiya\\! I'm the Singlish Translator bot, useful for anyone needing Singaporean English explanation and translation\\.
I accept the following commands\\.

`/definition <term>`: Fully define a Singlish term\\.
`/help`: Show this message\\.
`/start`: Show this message\\.
"""
	else:
		response = "I don't recognize that command\\. Use `/help` to see which I do."

	context.bot.send_message(
		chat_id=update.effective_chat.id,
		parse_mode=ParseMode.MARKDOWN_V2,
		text=response
	)

def term_definition(term, db, abbreviated=False):
	definition = db.term_definition(term)

	if definition is None:
		return

	if abbreviated and len(definition) > DEF_PREVIEW_LEN:
		definition = f"{definition[:DEF_PREVIEW_LEN]}..."

	return f"*{term}*: {telegram.utils.helpers.escape_markdown(definition, version=2)}"

def text_handler(update, context):
	singlish = translator.find_singlish(update.message.text)

	if len(singlish) == 0:
		return

	db = Database()

	response = [f"Hiya\\! @{telegram.utils.helpers.escape_markdown(update.effective_user.username)} used the following Singlish, which I've conveniently defined\\. Use `/definition <term>` to see more\\."]

	for term in singlish:
		response.append(term_definition(term, db, abbreviated=True))

	context.bot.send_message(
		chat_id=update.effective_chat.id,
		parse_mode=ParseMode.MARKDOWN_V2,
		text="\n\n".join(response)
	)

updater = Updater(token=config["token"])

dispatcher = updater.dispatcher
dispatcher.add_handler(MessageHandler(Filters.command, command_handler))
dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), text_handler))

updater.start_polling()
