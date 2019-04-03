from .language import UtteranceType
from .ner import NER
from . import utils
import wordnet_utils as wu

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
            Analyzer.LOG.debug("Couldn't parse input")
            return None

        for tree in forest:
            sentence_type = tree[0].label()

            if sentence_type == 'S':
                return StatementAnalyzer.analyze(chat)
            elif sentence_type == 'Q':
                return QuestionAnalyzer.analyze(chat)
            else:
                print("Error: ", sentence_type)


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

    @property
    def perspective(self):
        """
        Returns
        -------
        perspective: dict or None
        """


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

    @property
    def perspective(self):
        """
        Returns
        -------
        perspective: dict or None
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

        super(GeneralStatementAnalyzer, self).__init__(chat)

        rdf = {'subject': '', 'predicate': '', 'object': ''}
        cons = self.chat.last_utterance.parser.constituents

        rdf['subject'] = cons[0]['raw']

        if len(cons)>2 and cons[2]['label'] == 'PP':
            pp = cons[2]['raw'].split()[0]
            remainder = ''
            for rest in cons[2]['raw'].split()[1:]:
                remainder += rest + ' '
            rdf['predicate'] = utils.lemmatize(cons[1]['raw']) + '-' + pp
            rdf['object'] = remainder.strip()

        else:
            if cons[1]['label'] == 'MOD':
                rdf['object'] = rdf['predicate'].split()[1]
                rdf['predicate'] = rdf['predicate'].split()[0]

            elif cons[2]['label'] == 'CP': #recursive parse?
                rdf['predicate'] += ' ' + cons[2]['raw'].split()[1]
                for el in cons[2]['raw'].split()[2:]:
                    rdf['object'] += el+' '
                rdf['subject'] = cons[2]['raw'].split()[0]

            elif '-' not in rdf['predicate'] and len(rdf['predicate'].split())==1:
                rdf['predicate'] = utils.lemmatize(cons[1]['raw'])

            else:
                rdf['predicate'] = utils.lemmatize(cons[1]['raw'])
            if len(cons) > 2 and rdf['object']=='':
                rdf['object'] = cons[2]['raw']


        interpret_elements(cons, self.GRAMMAR)
        perspective = analyze_predicate(rdf['predicate'], self.GRAMMAR)

        if 'fix' in perspective:
            rdf['predicate'] = perspective['fix']

        rdf = utils.dereference_pronouns(self, rdf, self.GRAMMAR, self.chat.speaker)
        print(rdf)
        self._rdf = rdf
        self._perspective = perspective

    @property
    def rdf(self):
        """
        Returns
        -------
        rdf: dict or None
        """
        return self._rdf

    @property
    def perspective(self):
        """
        Returns
        -------
        perspective: dict or None
        """
        return self._perspective

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

        for el in cons:
            #print(el, cons[el])
            if cons[el]['label'].startswith('V'):
                rdf['predicate'] = cons[el]['raw']

            if cons[el]['label'] == 'PP':
                if 'structure' in cons[el]:
                    tree = cons[el]['structure']
                    for branch in tree:
                        for node in branch:
                            #print(node.label())
                            if node.label().startswith('N'):
                                rdf['subject'] = node.leaves()[0]
                            if node.label()=='IN':
                                rdf['predicate']+='_'+node.leaves()[0]

            elif cons[el]['label'] == 'NP':
                if el!=len(cons)-1:
                    rdf['subject'] = cons[el]['raw']
                else:
                    rdf['object'] = cons[el]['raw']

        analyze_predicate(rdf['predicate'])

        interpret_elements(cons, self.GRAMMAR)
        rdf = utils.dereference_pronouns(self, rdf, self.GRAMMAR, self.chat.speaker)
        self._rdf = rdf

    @property
    def rdf(self):
        """
        Returns
        -------
        rdf: dict or None
        """
        return self._rdf

def analyze_predicate(predicate, lexicon):
    sent = {}
    cert = {}
    polarity = 1

    for word in predicate.split():
        if word == 'not':
            polarity=-1
        word = utils.lemmatize(word)
        entry = utils.find(word, lexicon, 'verb')
        if entry:
            if 'sentiment' in entry:
                sent[word] = entry['sentiment']
            if 'certainty' in entry:
                cert[word] = entry['certainty']

    S = calculate_sentiment(sent)*polarity
    C = calculate_certainty(cert)
    perspective = {'sentiment': S, 'certainty': C, 'polarity': polarity}

    if polarity==-1:
        p = ''
        for word in predicate.split()[2:]:
            p+=word+' '
        p = p.strip()
        perspective['fix'] = p

    return perspective


def calculate_certainty(cert):
    C = 1
    for el in cert:
        C*=cert[el]
    return C

def calculate_sentiment(sent):
    if not len(sent):
        S=0
    else:
        S=1
        for el in sent:
            S*=sent[el]
    return S


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
        cons = self.chat.last_utterance.parser.constituents

        for el in cons:
            print(el, cons[el])

            if cons[el]['label'].startswith('V'):
                rdf['predicate'] = cons[el]['raw']

            if 'structure' in cons[el]:
                tree = cons[el]['structure']
                print(tree)

            if cons[el]['label'].startswith('N') or cons[el]['label']=='PRP':
                if rdf['subject']:
                    rdf['object'] = cons[el]['raw']
                else:
                    rdf['subject'] = cons[el]['raw']

        rdf = utils.dereference_pronouns(self, rdf, self.GRAMMAR, self.chat.speaker)
        self._rdf = rdf

    @property
    def rdf(self):
        """
        Returns
        -------
        rdf: dict or None
        """
        return self._rdf


def interpret_elements(cons, lexicon):
    for el in cons:
        # wordnet lookup
        if 'structure' in cons[el]:
            for word in cons[el]['raw'].split():
                label = utils.get_node_label(cons[el]['structure'], word)
                print('node label ',label)
                syn = wu.get_synsets(word, label)
                if syn: print(wu.get_lexname(syn[0]))
                #print(utils.get_uri(word))
        else:
            word = cons[el]['raw']
            label = cons[el]['label']
            syn = wu.get_synsets(word, label)
            if syn: print(wu.get_lexname(syn[0]))
        # TODO DBpedia lookup


def analyze(chat):
    analyzer = Analyzer.analyze(chat)

    if not analyzer:
        return "I cannot parse your input"

    Analyzer.LOG.debug("RDF {}".format(analyzer.rdf))

    if analyzer.utterance_type == UtteranceType.STATEMENT:
        if not utils.check_rdf_completeness(analyzer.rdf):
            #TODO intransitive verbs
            Analyzer.LOG.debug('incomplete statement RDF')
            return

    template = utils.write_template(chat.speaker, analyzer.rdf, chat.id, chat.last_utterance.turn,
                                    analyzer.utterance_type)

    if analyzer.utterance_type == UtteranceType.STATEMENT:
        perspective = analyzer.perspective
        print(perspective)
        for el in perspective:
            if el!='fix':
                template[el] = perspective[el]

    print(template)
    return template
