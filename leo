#!/usr/bin/env python3

import sys
import os
import requests
import re
from bs4 import BeautifulSoup

if __name__ == "__main__":
	if len(sys.argv) < 2:
		print("leo.py must be run with at least 1 parameter (word to translate)")
		sys.exit(1)

	url = 'https://dict.leo.org/englisch-deutsch/' + " ".join(sys.argv[1:])
	r = requests.get(url)

	soup = BeautifulSoup(r.text, "html.parser")

	def format_dict_line(s):
		s = re.sub(r"\.([\w\.]+) ", r". (\1) ", s)
		s = s.replace(" - ", ": ")

		s = re.sub(r"[\s\xa0]+", " ", s)

		s = re.sub("\u21d4 (\\w+)", r"\1", s)

		s = s.replace("|", "[", 1)
		s = s.replace("|", "]", 1)
		s = s.replace("|", "[", 1)
		s = s.replace("|", "]", 1)
		s = re.sub(r"\[ ", "[", s)
		s = re.sub(r" \]", "]", s)
		s = s.replace(")[",") [")

		s = s.strip()
		return s

	def align(table, delim="|"):
		max_widths = [0] * len(table[0])
		string_table = ""
		for row in table:
			for i, element in enumerate(row):
				if (width := len(element)) > max_widths[i]:
					max_widths[i] = width
		for i, row in enumerate(table):
			for j, element in enumerate(row):
				table[i][j] = element.ljust(max_widths[j])
			string_table += delim.join(table[i]) + "\n"
		return string_table

	os.system("")
	for tbody in soup.select("table.tblf1.tblf-fullwidth.tblf-alternate"):
		heading = tbody.find("h2").text
		table = tbody.find("tbody")
		print("\x1b[33m"+"#"*10, heading, "#"*10+"\x1b[0m")
		leo_entry = []
		for line in table:
			try:
				en = line.select("td[lang=en]")[0].text
				de = line.select("td[lang=de]")[0].text
				leo_entry.append([format_dict_line(en), format_dict_line(de)])
			except:
				continue
		try:
			print(align(leo_entry, " | "))
		except:
			continue


	# print("\x1b[3A")
	sys.exit(0)
