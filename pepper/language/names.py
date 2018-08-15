from pepper.sensor.asr import GoogleASR
from pepper.language.ner import NER
from nltk.metrics.distance import edit_distance


class NameParser:
    TAGS_OF_INTEREST = ['PERSON', 'LOCATION', 'ORGANISATION']

    def __init__(self, names, languages=('en-GB', 'nl-NL', 'es-ES'), max_name_distance=2.5, min_alternatives=4):
        self._names = names
        self._languages = languages
        self._asrs = [GoogleASR(language) for language in languages]

        self._max_name_distance = max_name_distance
        self._min_alternatives = min_alternatives

        self._tagger = NER()

    def parse_known(self, transcript):
        toi = None  # Transcript of Interest
        words = []

        for i, (string, confidence) in enumerate(transcript):
            for word, tag in self._tagger.tag(string):
                if tag in NameParser.TAGS_OF_INTEREST:
                    words.append((word, confidence))

                    if toi is None: toi = i

        if len(words) >= self._min_alternatives:
            closest_name = None
            closest = self._max_name_distance

            for name in self._names:
                distance = sum(edit_distance(name, word) * confidence for word, confidence in words) / float(len(words))
                if distance < closest:
                    closest_name = name
                    closest = distance

            if closest_name:
                return transcript[toi][0].replace(words[0][0], closest_name), transcript[toi][1]

        return transcript[0]

    def parse_new(self, audio):
        name_match = None
        name_match_confidence = 0

        for language, asr in zip(self._languages, self._asrs):
            transcript = asr.transcribe(audio)

            for i, (string, confidence) in enumerate(transcript):
                for word, tag in self._tagger.tag(string):
                    if tag in NameParser.TAGS_OF_INTEREST:
                        if confidence > name_match_confidence:
                            name_match = word
                            name_match_confidence = confidence

        if name_match:
            return name_match, name_match_confidence
