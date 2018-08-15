from pepper.language.ner import NER
from nltk.metrics.distance import edit_distance
import os


class NameParser:

    STANFORD_ROOT = os.path.join(os.path.dirname(__file__), 'stanford-ner')
    TAGS_OF_INTEREST = ['PERSON', 'LOCATION', 'ORGANISATION']
    MAX_NAME_DISTANCE = 3

    def __init__(self, names, languages = ("en-GB", 'nl-NL', 'es-ES')):
        self._names = names
        self._languages = languages
        self._tagger = NER()

    def parse(self, transcript, audio):

        toi = None  # Transcript of Interest
        words = []

        for i, (string, confidence) in enumerate(transcript):
            for word, tag in self._tagger.tag(string):
                if tag in NameParser.TAGS_OF_INTEREST:
                    words.append(word)

                    if toi is None: toi = i

        if words:
            closest_name = None
            closest = NameParser.MAX_NAME_DISTANCE

            for name in self._names:
                distance = sum(edit_distance(name, word) for word in words) / float(len(words))
                print(name, distance)
                if distance < closest:
                    closest_name = name
                    closest = distance

            print(transcript[toi])

            if closest_name:
                return transcript[toi][0].replace(words[0], closest_name), transcript[toi][1]

        return transcript[0]