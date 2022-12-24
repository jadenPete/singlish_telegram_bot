#!/usr/bin/env python

from bs4 import BeautifulSoup
import re

import db

BASE_URL = "http://www.mysmu.edu/faculty/jacklee"

def get_text_no_repeated_space(tag):
	text = re.sub(r" {2,}", " ", tag.get_text().strip())

	return "\n".join(sentence.strip() for sentence in text.split("\n"))

def scrape_subpages(soup):
	result = set()

	for anchor in soup.find_all("a"):
		if anchor.get("href") is None:
			continue

		if (match := re.match(r"\.\.\/(singlish_.+\.htm)(?:#.*)?$", anchor["href"])) is None:
			continue

		result.add(f"{BASE_URL}/{match[1]}")

	return result

def scrape_terms(soup):
	result = {}

	last_term = None

	for paragraph in soup.find_all("p"):
		term_tag = paragraph.select_one("a[name]")

		if term_tag is None:
			if last_term is None:
				continue

			term = last_term
		else:
			term = get_text_no_repeated_space(term_tag)

			if term.startswith("†"):
				term = term[len("†"):]

		if term == (definition := get_text_no_repeated_space(paragraph)):
			# The first paragraph is usually the subpage title

			continue

		if term in result:
			result[term] = f"{result[term]}\n\n{definition}"
		else:
			result[term] = definition

	return result

def scrape():
	if not db.singleton.finished_scraping():
		db.singleton.delete_term_cache()

		page = db.singleton.fetch_page(f"{BASE_URL}/Information/singlish_menu.htm")

		soup = BeautifulSoup(page, "html.parser")

		for subpage_url in scrape_subpages(soup):
			page = db.singleton.fetch_page(subpage_url)
			page = re.sub(r"[\r\n]|&nbsp;", " ", page)
			page = page.replace("<br>", "\n")

			soup = BeautifulSoup(page, "html.parser")

			dictionary = scrape_terms(soup)

			db.singleton.update_dictionary(dictionary)

			for term, definition in dictionary.items():
				print(f"{term}: {definition}\n")

		db.singleton.set_finished_scraping(True)

if __name__ == "__main__":
	scrape()
