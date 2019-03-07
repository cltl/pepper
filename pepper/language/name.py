from pepper.framework.sensor.asr import SynchronousGoogleASR, UtteranceHypothesis
from .ner import NER
from nltk.metrics.distance import edit_distance
from concurrent import futures


class NameParser:
    TAGS_OF_INTEREST = ['PERSON', 'LOCATION', 'ORGANISATION']

    TAGGER = None  # type: NER

    def __init__(self, names, languages=('en-GB', 'nl-NL', 'es-ES'), max_name_distance=2, min_alternatives=4):
        if not NameParser.TAGGER:
            NameParser.TAGGER = NER()

        self._names = names
        self._languages = languages
        self._asrs = [SynchronousGoogleASR(language) for language in languages]
        self._pool = futures.ThreadPoolExecutor(len(self._asrs))

        self._max_name_distance = max_name_distance
        self._min_alternatives = min_alternatives

    def parse_known(self, hypotheses):
        toi = None  # Transcript of Interest
        words = []

        for i, (hypothesis) in enumerate(hypotheses):
            for word, tag in self.TAGGER.tag(hypothesis.transcript):
                if tag in NameParser.TAGS_OF_INTEREST:
                    words.append((word, hypothesis.confidence))

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
                print("Closest Name:", closest_name)
                return UtteranceHypothesis(hypotheses[toi].transcript.replace(words[0][0], closest_name), hypotheses[toi].confidence)

        return hypotheses[0]

    def parse_new(self, audio):
        threads = [self._pool.submit(self._parse_new, asr, audio) for asr in self._asrs]
        results = [result.result() for result in futures.as_completed(threads)]

        best_name = None
        best_confidence = 0.0

        for result in results:
            if result:
                name, confidence = result
                if confidence > best_confidence:
                    best_name = name
                    best_confidence = confidence

        if best_name:
            return best_name, best_confidence

    def _parse_new(self, asr, audio):
        transcript = asr.transcribe(audio)

        for i, hypothesis in enumerate(transcript):
            for word, tag in self.TAGGER.tag(hypothesis.transcript):
                if tag in NameParser.TAGS_OF_INTEREST:
                    return word, hypothesis.confidence
