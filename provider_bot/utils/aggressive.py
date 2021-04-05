import re

with open('./provider_bot/utils/aggressive.txt') as f:
    words = {w.lower().strip() for w in f.readlines()}


def is_aggressive(text):
    text = re.sub('\!\?\,\;\.', '', text).lower().split(' ')
    for w in text:
        if w in words:
            return True
    return False