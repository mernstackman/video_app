import re
import emoji
import random
import nltk
from nltk.corpus import wordnet
import logging

logging.basicConfig(filename='crop_debug.log', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

SYNONYMS = {
    'fight': ['battle', 'brawl', 'clash', 'duel', 'scuffle'],
    'scene': ['sequence', 'clip', 'moment', 'segment'],
    'win': ['triumph', 'victory', 'success'],
    'wins': ['triumphs', 'victories'],
    'winner': ['champion', 'victor'],
    'gym': ['fitness center', 'training area'],
    'fighter': ['combatant', 'warrior', 'boxer'],
    'fighting': ['battling', 'clashing', 'sparring']
}

def clean_title(title):
    title = emoji.replace_emoji(title, replace='')
    title = re.sub(r'[^\w\s-]', '', title)
    title = re.sub(r'\s+', ' ', title).strip()
    return title

def get_synonym(word):
    word_lower = word.lower()
    if word_lower in SYNONYMS:
        return random.choice(SYNONYMS[word_lower])
    synsets = wordnet.synsets(word_lower)
    if synsets:
        synonyms = [lemma.name() for synset in synsets for lemma in synset.lemmas()]
        synonyms = [s.replace('_', ' ') for s in synonyms if s != word_lower]
        return random.choice(synonyms) if synonyms else word
    return word

def auto_rename_title(original_title):
    cleaned = clean_title(original_title)
    return f"Best {cleaned} Fight Scene"