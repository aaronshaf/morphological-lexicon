#!/usr/bin/env python3

from collections import defaultdict
import os.path
import re
import sys
import unicodedata


from morphgnt import filesets
from morphgnt.utils import sorted_items


fs = filesets.load("filesets.yaml")


ACUTE = u"\u0301"
GRAVE = u"\u0300"
CIRCUMFLEX = u"\u0342"


def strip_accents(w):
    return "".join(
        unicodedata.normalize("NFC", "".join(
            component for component in unicodedata.normalize("NFD", ch) if component not in [ACUTE, GRAVE, CIRCUMFLEX]
        )) for ch in w
    )


# tense_voice -> list of dicts mapping person_number to ending (or ?)
ENDINGS = defaultdict(list)

with open(os.path.join(os.path.dirname(__file__), "ending-paradigms.txt")) as f:
    num = 0
    for line in f:
        line = line.split("#")[0].strip()
        num += 1
        if not line:
            continue
        tense_voice, rest = line.strip().split(":")
        endings = dict(zip(["1S", "2S", "3S", "1P", "2P", "3P", "num"], [i.strip() for i in rest.split(",")] + [num]))
        ENDINGS[tense_voice].append(endings)


fs = filesets.load("filesets.yaml")

# lemma -> tense_voice -> person_number -> set of forms
forms = defaultdict(lambda: defaultdict(lambda: defaultdict(set)))


def equal(lst):
    """
    are all elements of lst equal?
    """
    return lst.count(lst[0]) == len(lst)


for row in fs["sblgnt-lexemes"].rows():
    if row["ccat-pos"] == "V-":
        mood = row["ccat-parse"][3]
        if mood in "I":
            person_number = row["ccat-parse"][0] + row["ccat-parse"][5]
            tense_voice = row["ccat-parse"][1:3]
            forms[row["lemma"]][tense_voice][person_number].add(strip_accents(row["norm"]))
        elif mood in "DSO":
            pass
        elif mood in "P":
            pass
        elif mood in "N":
            pass
        else:
            raise ValueError


SKIP_LIST = [
    "σαβαχθάνι",
    "χρή",
]

for lemma, form_dict in sorted_items(forms):
    if lemma in SKIP_LIST:
        continue

    print()
    for tense_voice in sorted(form_dict):
        first_singular_forms = set()
        for endings in ENDINGS[tense_voice]:
            fail = False
            stems = []
            num = endings["num"]
            first_singular = endings["1S"]
            for person_number, ending in sorted(endings.items()):
                if person_number == "num":
                    continue
                ending = sorted(ending.split("/"))
                x = sorted(form_dict[tense_voice].get(person_number, "?"))
                if ending == ["?"] or x == ["?"]:
                    continue
                if len(ending) != len(x):
                    fail = True
                    break
                stem_possibilities = set()
                for a, b in zip(ending, x):
                    regex = a.replace("?", "\\?").replace("(", "\\(").replace(")", "\\)") + "$"
                    if not re.search(regex, b):
                        fail = True
                        break
                    stem_possibilities.add(re.sub(regex, "", b))
                if len(stem_possibilities) == 1:
                    stems.append(list(stem_possibilities)[0])
                else:
                    fail = True
                    break
            if stems and not fail and equal(stems):
                first_singular_forms.add(stems[0] + first_singular)

        if len(first_singular_forms) == 0:
            print()
            print(lemma, tense_voice)
            print(form_dict[tense_voice])
            print("no rules matched")
            sys.exit(1)
        print("{} {} {}".format(lemma, tense_voice, "|".join(form for form in first_singular_forms)))
