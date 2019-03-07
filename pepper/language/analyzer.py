from .language import UtteranceType
from .ner import NER
from . import utils

from pepper import logger

import json
import os


class Analyzer(object):
    # Load Grammar Json
    GRAMMAR_JSON = os.path.join(os.path.dirname(__file__), 'data', 'lexicon.json')
    with open(GRAMMAR_JSON) as json_file:
        GRAMMAR = json.load(json_file)

    # Load Stanford Named Entity Recognition Server
    NER = None  # type: NER

    LOG = logger.getChild(__name__)

    def __init__(self, chat):
        """
        Abstract Analyzer Object: call Analyzer.analyze(utterance) factory function

        Parameters
        ----------
        chat: Chat
            Chat to be analyzed
        """

        if not Analyzer.NER:
            Analyzer.NER = NER('english.muc.7class.distsim.crf.ser')

        self._chat = chat

    @staticmethod
    def analyze(chat):
        """
        Analyzer factory function

        Find appropriate Analyzer for this utterance

        Parameters
        ----------
        chat: Chat
            Chat to be analyzed

        Returns
        -------
        analyzer: Analyzer
            Appropriate Analyzer Subclass
        """

        forest = chat.last_utterance.parser.forest

        if not forest:
            Analyzer.LOG.info("Couldn't parse input")
            return None

        for tree in forest:
            sentence_type = tree[0].label()

            if sentence_type == 'S':
                return StatementAnalyzer.analyze(chat)
            elif sentence_type == 'Q':
                return QuestionAnalyzer.analyze(chat)
            else:
                print("Error: ", sentence_type)

        '''
        if chat.last_utterance.tokens:
            first_token = chat.last_utterance.tokens[0]

            question_words = Analyzer.GRAMMAR['question words'].keys()
            to_be = Analyzer.GRAMMAR['to be'].keys()
            modal_verbs = Analyzer.GRAMMAR['modal_verbs']

            question_cues = question_words + to_be + modal_verbs

            # Classify Utterance as Question / Statement
            if first_token in question_cues:
                return QuestionAnalyzer.analyze(chat)
            else:
                return StatementAnalyzer.analyze(chat)
        else:
            raise ValueError("Utterance should have at least one element")
        '''

    @property
    def chat(self):
        """
        Returns
        -------
        chat: Chat
            Chat to be analyzed
        """
        return self._chat

    @property
    def utterance_type(self):
        """
        Returns
        -------
        utterance_type: UtteranceType
            Utterance Type
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

        # TODO: Implement here!

        return None


class StatementAnalyzer(Analyzer):
    """Abstract StatementAnalyzer Object: call StatementAnalyzer.analyze(utterance) factory function"""

    @staticmethod
    def analyze(chat):
        """
        StatementAnalyzer factory function

        Find appropriate StatementAnalyzer for this utterance

        Parameters
        ----------
        chat: Chat
            Chat to be analyzed

        Returns
        -------
        analyzer: StatementAnalyzer
            Appropriate StatementAnalyzer Subclass
        """

        return GeneralStatementAnalyzer(chat)

    @property
    def utterance_type(self):
        """
        Returns
        -------
        utterance_type: UtteranceType
            Utterance Type (Statement)
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
    def __init__(self, chat):
        """
        General Statement Analyzer

        Parameters
        ----------
        chat: Chat
            Chat to be analyzed
        """
        dict = {}
        super(GeneralStatementAnalyzer, self).__init__(chat)

        rdf = {'predicate': '', 'subject': '', 'object': ''}
        cons = self.chat.last_utterance.parser.constituents

        rdf['subject'] = cons[0]['raw']

        if cons[2]['label'] == 'PP':
            pp = cons[2]['raw'].split()[0]
            remainder = ''
            for rest in cons[2]['raw'].split()[1:]:
                remainder += rest + ' '
            rdf['predicate'] = cons[1]['raw'] + '-' + pp
            rdf['object'] = remainder.strip()
        else:
            rdf['predicate'] = cons[1]['raw']
            rdf['object'] = cons[2]['raw']

        print(rdf)

        '''
                    #position += 1
                    #print(node.label(), node.leaves()[0])
                    if node.label().startswith('V') and \
                            (node.leaves()[0].lower() or node.leaves()[0].lower()[:-1]) in self.GRAMMAR['verbs']:
                        rdf['predicate'] += node.leaves()[0] + ' '

                    elif node.leaves()[0]=='from':
                        if rdf['predicate'].strip() in self.GRAMMAR['verbs']['to be']:
                            rdf['predicate'] = 'is_from'

                    elif node.leaves()[0].lower() in self.GRAMMAR['pronouns'] and position < len(
                            chat.last_utterance.tokens):
                        rdf['subject'] += node.leaves()[0] + ' '
                        dict['pronoun'] = self.GRAMMAR['pronouns'][node.leaves()[0].lower()]
                        rdf['subject'] = utils.fix_pronouns(dict, self.chat.speaker)

                    elif node.label().startswith('N') and position == len(chat.last_utterance.tokens):
                        rdf['object'] += node.leaves()[0] + ' '
                    '''

        if rdf['object'].lower() in self.GRAMMAR['pronouns']['subject']:
            dict['pronoun'] = self.GRAMMAR['pronouns']['subject'][rdf['object'].lower()]
            rdf['object'] = utils.fix_pronouns(dict, self.chat.speaker)

        if rdf['subject'].lower() in self.GRAMMAR['pronouns']['subject']:
            dict['pronoun'] = self.GRAMMAR['pronouns']['subject'][rdf['subject'].lower()]
            rdf['subject'] = utils.fix_pronouns(dict, self.chat.speaker)

        print(rdf)

        self._rdf = rdf

    @property
    def rdf(self):
        """
        Returns
        -------
        rdf: dict or None
        """
        return self._rdf


class ObjectStatementAnalyzer(StatementAnalyzer):
    def __init__(self, chat):
        """
        Object Statement Analyzer

        Parameters
        ----------
        chat: Chat
        """

        super(ObjectStatementAnalyzer, self).__init__(chat)

        # TODO: Implement Chat -> RDF

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
    """Abstract QuestionAnalyzer Object: call QuestionAnalyzer.analyze(utterance) factory function"""

    @staticmethod
    def analyze(chat):
        """
        QuestionAnalyzer factory function

        Find appropriate QuestionAnalyzer for this utterance

        Parameters
        ----------
        chat: Chat
            Chat to be analyzed

        Returns
        -------
        analyzer: QuestionAnalyzer
            Appropriate QuestionAnalyzer Subclass
        """
        if chat.last_utterance.tokens:
            first_word = chat.last_utterance.tokens[0]
            if first_word.lower() in Analyzer.GRAMMAR['question words']:
                return WhQuestionAnalyzer(chat)
            else:
                return VerbQuestionAnalyzer(chat)

    @property
    def utterance_type(self):
        """
        Returns
        -------
        utterance_type: UtteranceType
            Utterance Type (Question)
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
    def __init__(self, chat):
        """
        Wh-Question Analyzer

        Parameters
        ----------
        chat: Chat
        """

        super(WhQuestionAnalyzer, self).__init__(chat)

        rdf = {'predicate': '', 'subject': '', 'object': ''}
        cons = self.chat.last_utterance.parser.constituents
        dict = {}

        for el in cons:
            print(el, cons[el])

        if cons[3]['label'].startswith('V'):
            rdf['predicate'] = cons[3]['raw']+'s'

        if cons[2]['label'] == 'NP':
            rdf['subject'] = cons[2]['raw']

        if rdf['object'].lower() in self.GRAMMAR['pronouns']['subject']:
            dict['pronoun'] = self.GRAMMAR['pronouns']['subject'][rdf['object'].lower()]
            rdf['object'] = utils.fix_pronouns(dict, self.chat.speaker)

        if rdf['subject'].lower() in self.GRAMMAR['pronouns']['subject']:
            dict['pronoun'] = self.GRAMMAR['pronouns']['subject'][rdf['subject'].lower()]
            rdf['subject'] = utils.fix_pronouns(dict, self.chat.speaker)

        print(rdf)



        '''
        for tree in chat.last_utterance.parsed_tree[0]:
            for branch in tree:
                for node in branch:
                    for leaf in node.leaves():

                        position += 1
                        # print(node.label(), leaf)

                        if node.label().startswith('V') and \
                                (leaf.lower() in self.GRAMMAR['verbs'] or leaf.lower()[:-1] in self.GRAMMAR['verbs']):
                            rdf['predicate'] += leaf + ' '

                        elif leaf.lower() in self.GRAMMAR['pronouns'] and position < len(chat.last_utterance.tokens):
                            rdf['subject'] += leaf + ' '
                            dict['pronoun'] = self.GRAMMAR['pronouns'][leaf.lower()]

                        elif node.label().startswith('N') and position == len(chat.last_utterance.tokens):
                            rdf['object'] += leaf + ' '

                        elif leaf.lower() == 'from':
                            rdf['predicate'] = 'is_from'

        for el in rdf:
            rdf[el] = rdf[el].strip()

        if 'pronoun' in dict:
            rdf['subject'] = utils.fix_pronouns(dict, self.chat.speaker)
        
        '''


        self._rdf = rdf

    @property
    def rdf(self):
        """
        Returns
        -------
        rdf: dict or None
        """
        return self._rdf


# verb question rules:
class VerbQuestionAnalyzer(QuestionAnalyzer):
    def __init__(self, chat):
        """
        Verb Question Analyzer

        Parameters
        ----------
        chat: Chat
        """

        super(VerbQuestionAnalyzer, self).__init__(chat)

        rdf = {'predicate': '', 'subject': '', 'object': ''}
        position = 0
        dict = {}

        for tree in chat.last_utterance.parser.forest[0]:
            for branch in tree:
                for node in branch:
                    position += 1
                    # print(node.label(), node.leaves()[0])
                    if node.label().startswith('V') and node.leaves()[0].lower() in self.GRAMMAR['verbs']:
                        rdf['predicate'] += node.leaves()[0] + ' '

                    elif node.leaves()[0].lower() in self.GRAMMAR['pronouns'] and position < len(
                            chat.last_utterance.tokens):
                        rdf['subject'] += node.leaves()[0] + ' '
                        dict['pronoun'] = self.GRAMMAR['pronouns'][node.leaves()[0].lower()]

                    elif node.label().startswith('N') and position == len(chat.last_utterance.tokens):
                        rdf['object'] += node.leaves()[0] + ' '

        for el in rdf:
            rdf[el] = rdf[el].strip()

        if rdf['object'].lower() in self.GRAMMAR['pronouns']:
            dict['pronoun'] = self.GRAMMAR['pronouns'][rdf['object'].lower()]
            rdf['object'] = utils.fix_pronouns(dict, self.chat.speaker)

        if rdf['subject'].lower() in self.GRAMMAR['pronouns']:
            dict['pronoun'] = self.GRAMMAR['pronouns'][rdf['subject'].lower()]
            rdf['subject'] = utils.fix_pronouns(dict, self.chat.speaker)

        print(rdf)
        self._rdf = rdf

    @property
    def rdf(self):
        """
        Returns
        -------
        rdf: dict or None
        """
        return self._rdf


def analyze(chat):
    analyzer = Analyzer.analyze(chat)

    if not analyzer:
        return "I cannot parse your input"

    if analyzer.rdf['predicate'] in analyzer.GRAMMAR['verbs']:
        analyzer.rdf['predicate'] += 's'

    if analyzer.utterance_type == UtteranceType.STATEMENT:
        if not utils.check_rdf_completeness(analyzer.rdf):
            print('incomplete statement RDF')
            return

    template = utils.write_template(chat.speaker, analyzer.rdf, chat.id, chat.last_utterance.turn,
                                    analyzer.utterance_type)
    #print(template)

    return template
