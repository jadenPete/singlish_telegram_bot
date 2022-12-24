import sqlite3
import urllib.request

class Database:
	def __init__(self, name="singlish_telegram_bot.db"):
		self.conn = sqlite3.connect(name)
		self.cur = self.conn.cursor()

	def create_schema(self):
		self.cur.execute(
			"""
CREATE TABLE IF NOT EXISTS page_cache (
	url TEXT PRIMARY KEY,
	content TEXT NOT NULL
);"""
		)

		self.cur.execute(
			"""
CREATE TABLE IF NOT EXISTS term_cache (
	term TEXT PRIMARY KEY,
	definition TEXT NOT NULL
);"""
		)

		self.cur.execute(
			"""
CREATE TABLE IF NOT EXISTS term_config (
	id INTEGER PRIMARY KEY CHECK (id = 0),
	finished BOOLEAN NOT NULL
);"""
		)

		self.conn.commit()

	def delete_term_cache(self):
		self.cur.execute("DELETE FROM term_cache;")
		self.conn.commit()

	def fetch_page(self, url):
		self.cur.execute("SELECT content FROM page_cache WHERE url = ?;", (url,))

		if (row := self.cur.fetchone()) is None:
			content = urllib.request.urlopen(url).read().decode()

			self.cur.execute("INSERT INTO page_cache VALUES (?, ?);", (url, content))
			self.conn.commit()
		else:
			content = row[0]

		return content

	def finished_scraping(self):
		self.cur.execute("SELECT finished FROM term_config;")

		return (row := self.cur.fetchone()) is not None and row[0]

	def set_finished_scraping(self, value):
		self.cur.execute(
			"""
INSERT INTO term_config (id, finished)
	VALUES (0, ?)
	ON CONFLICT (id) DO UPDATE SET finished = EXCLUDED.finished;""", (value,)
			)

		self.conn.commit()

	def term_definition(self, term):
		self.cur.execute("SELECT definition FROM term_cache WHERE term = ?;", (term,))

		if (row := self.cur.fetchone()) is not None:
			return row[0]

	def terms(self):
		self.cur.execute("SELECT term FROM term_cache;")

		return [row[0] for row in self.cur.fetchall()]

	def update_dictionary(self, dictionary):
		for term, definition in dictionary.items():
			self.cur.execute(
				"""
INSERT INTO term_cache VALUES (?, ?)
	ON CONFLICT (term) DO UPDATE SET definition = EXCLUDED.definition;""", (term, definition)
			)

		self.conn.commit()

singleton = Database()
