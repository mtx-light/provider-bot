import pymorphy2
import re

tones = {}

morph = pymorphy2.MorphAnalyzer(lang='uk')

with open('./tone-dict-uk.tsv') as tone_dict:
    for line in tone_dict.readlines():
        line = line.split('\t')
        normal_form = morph.parse(line[0])[0].normal_form
        tones[normal_form] = int(line[1])


def tone(text):
    score = 0
    count = 0
    words = re.sub('\!\?\,\;', '', text).lower().split(' ')
    for word in words:
        normal_form = morph.parse(word)[0].normal_form
        if normal_form in tones:
            print(normal_form)
            score += tones.get(normal_form, 0)
            count += 1
    return score / count if count else 0
