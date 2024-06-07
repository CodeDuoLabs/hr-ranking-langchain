from typing import List

import re


def find_whole_word(w):
    return re.compile(r"\b({0})\b".format(w), flags=re.IGNORECASE).search


def skill_check(doc: str, keywords: List[str]) -> bool:
    content = doc.lower()
    matches = False
    for keyword in keywords:
        if find_whole_word(keyword)(content):
            matches = True
            break
    return matches