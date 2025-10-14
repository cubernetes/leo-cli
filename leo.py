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
    first_lang='en'
    second_lang='de'
    lang_url = 'https://dict.leo.org/englisch-deutsch/'
    for arg in sys.argv:
        if arg == '--color':
            force_color = True
        elif arg == '--eng-ger' or arg == '--ger-eng':
            lang_url = 'https://dict.leo.org/englisch-deutsch/'
            first_lang='en'
            second_lang='de'
        elif arg == '--spa-eng' or arg == '--eng-spa':
            lang_url = 'https://dict.leo.org/spanish-english/'
            first_lang='es'
            second_lang='en'
        elif arg == '--ger-spa' or arg == '--spa-ger':
            lang_url = 'https://dict.leo.org/alem%C3%A1n-espa%C3%B1ol/'
            first_lang='es'
            second_lang='de'
        elif arg == '--fre-ger' or arg == '--ger-fre':
            lang_url = 'https://dict.leo.org/franz%C3%B6sisch-deutsch/'
            first_lang='fr'
            second_lang='de'
        elif arg == '--eng-fre' or arg == '--fre-eng':
            lang_url = 'https://dict.leo.org/anglais-fran%C3%A7ais/'
            first_lang='en'
            second_lang='fr'
        elif arg == '--rus-ger' or arg == '--ger-rus':
            lang_url = 'https://dict.leo.org/%D0%BD%D0%B5%D0%BC%D0%B5%D1%86%D0%BA%D0%B8%D0%B9-%D1%80%D1%83%D1%81%D1%81%D0%BA%D0%B8%D0%B9/'
            first_lang='ru'
            second_lang='de'
        elif arg == '--rus-eng' or arg == '--eng-rus':
            lang_url = 'https://dict.leo.org/russian-english/'
            first_lang='en'
            second_lang='ru'
        else:
            args.append(arg)
    if len(args) < 2:
        print(f"Usage: leo [--color] [--<lang>-<lang>] WORD [WORD...]")
        print(f"         WORDs will be concatenated using spaces")
        print(f"         --color forces color output")
        print(f"         <lang> can be one of spa, eng, ger, fre, rus.")
        print(f"         Only some combinations are allowed.")
        sys.exit(1)

    url = lang_url + ' '.join(args[1:])

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
                    en_tag = line.select(f"td[lang={first_lang}]")[0]
                    de_tag = line.select(f"td[lang={second_lang}]")[0]
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
