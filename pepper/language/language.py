from pepper.language.ner import NER

import logging
import enum
import json
import re
import os


class UtteranceType(enum.Enum):
    STATEMENT = 0
    QUESTION = 1


class UtteranceID(object):
    def __init__(self, chat_id, chat_turn):
        """
        Parameters
        ----------
        chat_id: int
        chat_turn: int
        """
        self._chat_id = chat_id
        self._chat_turn = chat_turn

    @property
    def chat_id(self):
        """
        Returns
        -------
        chat_id: int
        """
        return self._chat_id

    @property
    def chat_turn(self):
        """
        Returns
        -------
        chat_turn: int
        """
        return self._chat_turn


class Utterance(object):
    def __init__(self, transcript, speaker, utterance_id):
        """
        Parameters
        ----------
        transcript: str
        speaker: str
        utterance_id: UtteranceID
        """

        # TODO: Add Viewed Objects!

        self._tokens = self._clean(self._tokenize(transcript))
        self._speaker = speaker
        self._utterance_id = utterance_id

    @property
    def tokens(self):
        """
        Returns
        -------
        transcript: str
        """
        return self._tokens

    @property
    def speaker(self):
        """
        Returns
        -------
        speaker: str
        """
        return self._speaker

    @property
    def utterance_id(self):
        """
        Returns
        -------
        utterance_id: UtteranceID
        """
        return self._utterance_id

    def _tokenize(self, transcript):
        """
        Parameters
        ----------
        transcript: str

        Returns
        -------
        tokens: list of str
            list of cleaned tokens
                - remove contractions
        """

        tokens_raw = transcript.split()
        tokens = []
        for word in tokens_raw:
            clean_word = re.sub('[?!]', '', word)
            tokens.append(clean_word.lower())
        return tokens

    def _clean(self, tokens):
        """
        Parameters
        ----------
        tokens: list of str

        Returns
        -------
        cleaned_tokens: list of str
        """
        # TODO: Remove Contractions

        return tokens


class Analyzer(object):

    GRAMMAR_JSON = os.path.join(os.path.dirname(__file__), 'grammar.json')
    with open(GRAMMAR_JSON) as json_file:
        GRAMMAR = json.load(json_file)['grammar']

    STANFORD_NER = NER('english.muc.7class.distsim.crf.ser')

    def __init__(self, utterance):
        """
        Parameters
        ----------
        utterance: Utterance
        """

        self._utterance = utterance
        self._log = logging.getLogger(self.__class__.__name__)

    @staticmethod
    def analyze(utterance):
        """
        Classify Utterance into Question / Statement

        Parameters
        ----------
        utterance: Utterance

        Returns
        -------
        analyzer: Analyzer
        """

        if utterance.tokens:
            first_token = utterance.tokens[0]

            question_words = Analyzer.GRAMMAR['question words'].keys()
            to_be = Analyzer.GRAMMAR['to be'].keys()
            modal_verbs = Analyzer.GRAMMAR['modal verbs']

            question_cues = question_words + to_be + modal_verbs

            if first_token in question_cues:
                return QuestionAnalyzer.analyze(utterance)
            else:
                return StatementAnalyzer.analyze(utterance)

    @property
    def log(self):
        """
        Returns
        -------
        log: logging.Logger
        """
        return self._log

    @property
    def utterance(self):
        """
        Returns
        -------
        utterance: Utterance
        """
        return self._utterance

    @property
    def utterance_type(self):
        """
        Returns
        -------
        utterance_type: UtteranceType
        """
        return NotImplementedError()

    @property
    def rdf(self):
        """
        Returns
        -------
        rdf: dict or None
        """
        raise NotImplementedError()

    @property
    def template(self):
        """
        Returns
        -------
        template: dict or None
        """
        raise NotImplementedError()


class StatementAnalyzer(Analyzer):
    @staticmethod
    def analyze(utterance):
        return GeneralStatementAnalyzer(utterance)

    @property
    def utterance_type(self):
        """
        Returns
        -------
        utterance_type: UtteranceType
        """
        return UtteranceType.STATEMENT

    @property
    def rdf(self):
        """
        Returns
        -------
        rdf: dict or None
        """
        raise NotImplementedError()


class GeneralStatementAnalyzer(StatementAnalyzer):
    def __init__(self, utterance):
        """
        Parameters
        ----------
        utterance: Utterance
        """

        super(GeneralStatementAnalyzer, self).__init__(utterance)

        # TODO: Implement Utterance -> RDF

        self._rdf = {}

    @property
    def rdf(self):
        """
        Returns
        -------
        rdf: dict or None
        """
        return self._rdf


class ObjectStatementAnalyzer(StatementAnalyzer):
    def __init__(self, utterance):
        """
        Parameters
        ----------
        utterance: Utterance
        """

        super(ObjectStatementAnalyzer, self).__init__(utterance)

        # TODO: Implement Utterance -> RDF

        self._rdf = {}

    @property
    def rdf(self):
        """
        Returns
        -------
        rdf: dict or None
        """
        return self._rdf


class QuestionAnalyzer(Analyzer):
    @staticmethod
    def analyze(utterance):
        if utterance.tokens:
            first_word = utterance.tokens[0]

            if first_word in Analyzer.GRAMMAR['question words']:
                return WhQuestionAnalyzer(utterance)
            else:
                return VerbQuestionAnalyzer(utterance)

    @property
    def utterance_type(self):
        """
        Returns
        -------
        utterance_type: UtteranceType
        """
        return UtteranceType.QUESTION

    @property
    def rdf(self):
        """
        Returns
        -------
        rdf: dict or None
        """
        raise NotImplementedError()


class WhQuestionAnalyzer(QuestionAnalyzer):
    def __init__(self, utterance):
        """
        Parameters
        ----------
        utterance: Utterance
        """

        super(WhQuestionAnalyzer, self).__init__(utterance)

        # TODO: Implement Utterance -> RDF

        self._rdf = {}

    @property
    def rdf(self):
        """
        Returns
        -------
        rdf: dict or None
        """
        return self._rdf


class VerbQuestionAnalyzer(QuestionAnalyzer):
    def __init__(self, utterance):
        """
        Parameters
        ----------
        utterance: Utterance
        """

        super(VerbQuestionAnalyzer, self).__init__(utterance)

        # TODO: Implement Utterance -> RDF

        self._rdf = {}

    @property
    def rdf(self):
        """
        Returns
        -------
        rdf: dict or None
        """
        return self._rdf


if __name__ == '__main__':
    utterance = Utterance("I like bananas", "Bram", UtteranceID(0, 0))
    analyzer = Analyzer.analyze(utterance)

    print(analyzer)