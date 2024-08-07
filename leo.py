#! /usr/bin/env python3

import os
import re
import sys
import readline

import requests
from bs4 import BeautifulSoup, Tag

if __name__ == "__main__":
    args = []
    force_color = False
    for arg in sys.argv:
        if arg == '--color':
            force_color = True
        else:
            args.append(arg)
    if len(args) < 2:
        print(f"Usage: leo [--color] WORD [WORD...]")
        print(f"Note: WORDs will be concatenated using spaces")
        print(f"Note: --color forces color output")
        sys.exit(1)

    url = 'https://dict.leo.org/englisch-deutsch/' + " ".join(sys.argv[1:])
    r = requests.get(url)

    soup = BeautifulSoup(r.text, "html.parser")

    def format_dict_line(s):
        s = re.sub(r"\.([\w\.]+) ", r". (\1) ", s)
        s = s.replace(" - ", ": ")

        s = re.sub(r"[\s\xa0]+", " ", s) # nbsp == "\xa0"

        s = re.sub("\u21d4 (\\w+)", r"\1", s)

        s = s.replace("|", "[", 1)
        s = s.replace("|", "]", 1)
        s = s.replace("|", "[", 1)
        s = s.replace("|", "]", 1)
        s = re.sub(r"\[ ", "[", s)
        s = re.sub(r" \]", "]", s)
        s = s.replace(")[",") [")
        if re.search(r"\SespAE ", s) and re.search(r"\SespBE ?", s):
            s = re.sub(r"(?<=\S)espAE ", " (espAE) ", s)
            s = re.sub(r"(?<=\S)espBE( )?", r" (espBE)\1", s)
        if re.search(r"\SAE ", s) and re.search(r"\SBE ?", s):
            s = re.sub(r"(?<=\S)AE ", " (AE) ", s)
            s = re.sub(r"(?<=\S)BE( )?", r" (BE)\1", s)
        s = re.sub(" (Pron|Adj|Adv).($| )", r" (\1.)\2", s)

        s = s.strip()
        return s

    def align(table, delim="|"):
        max_widths = [0] * len(table[0])
        string_table = ""
        for row in table:
            for i, element in enumerate(row): # j = 0..1 (2 columns)
                if (width := max(map(len, element.split("<NL>")))) > max_widths[i]:
                    max_widths[i] = width
        for i, row in enumerate(table):
            lines = []
            for j, element in enumerate(row): # j = 0..1 (2 columns)
                parts = element.split("<NL>")
                lines.append([])
                for part in parts:
                    lines[-1].append(part.ljust(max_widths[j]))
            max_lines = 0
            for line in lines:
                max_lines = max(max_lines, len(line))
            for i, line in enumerate(lines):
                if len(line) < max_lines:
                    lines[i] += [''] * (max_lines - len(line))
            first = True
            for line in zip(*lines):
                if first:
                    string_table += delim.join(line) + "\n"
                else:
                    string_table += " ".join(line) + "\n"
                first = False
        return string_table

    os.system("")
    for tbody in soup.select("table.tblf1.tblf-fullwidth.tblf-alternate")[::-1]:
        h2_tag = tbody.find("h2")
        if not h2_tag:
            continue
        heading = h2_tag.text
        table = tbody.find("tbody")
        if not table:
            continue
        if os.isatty(1) or force_color:
            print(end="\x1b[33m")
        print("#"*10, heading, "#"*10)
        if os.isatty(1) or force_color:
            print(end="\x1b[0m")
        leo_entry = []
        for line in table:
            try:
                if isinstance(line, Tag):
                    en_tag = line.select("td[lang=en]")[0]
                    de_tag = line.select("td[lang=de]")[0]
                    en_br = en_tag.select_one("br")
                    de_br = de_tag.select_one("br")
                    if en_br is not None:
                        en_br.replace_with("<NL>")
                    if de_br is not None:
                        de_br.replace_with("<NL>")
                    en = en_tag.text
                    de = de_tag.text
                else:
                  en = de = ''
                if en and de:
                    leo_entry.append([format_dict_line(en), format_dict_line(de)])
            except:
                continue
        try:
            print(align(leo_entry, " | "))
        except:
            continue


    # print("\x1b[3A")
    sys.exit(0)
