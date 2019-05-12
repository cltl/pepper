from .ner import NER
from .utils.helper_functions import lemmatize, dereference_pronouns, find, get_node_label
from .utils.atoms import UtteranceType
import wordnet_utils as wu

from pepper import logger

import urllib
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

        if len(cons) > 2 and cons[2]['label'] == 'PP':
            pp = cons[2]['raw'].split()[0]
            remainder = ''
            for rest in cons[2]['raw'].split()[1:]:
                remainder += rest + ' '
            rdf['predicate'] = lemmatize(cons[1]['raw'], 'v') + '-' + pp
            # print('trying to lemmatize ', cons[1]['raw'], utils.lemmatize(cons[1]['raw'],'v'))
            rdf['object'] = remainder.strip()

        else:
            if cons[1]['label'] == 'MOD':
                if ' ' in rdf['predicate']:
                    rdf['object'] = rdf['predicate'].split()[1]
                    rdf['predicate'] = rdf['predicate'].split()[0]
                else:
                    for el in cons[1]['structure']:
                        for eli in el:
                            if rdf['predicate']:
                                rdf['object'] = eli.leaves()[0]
                            else:
                                rdf['predicate'] = eli.leaves()[0]

            elif cons[2]['label'] == 'CP':  # recursive parse?
                rdf['predicate'] += ' ' + cons[2]['raw'].split()[1]
                for el in cons[2]['raw'].split()[2:]:
                    rdf['object'] += el + ' '
                rdf['subject'] = cons[2]['raw'].split()[0]

            else:
                rdf['predicate'] = lemmatize(cons[1]['raw'],'v')

            '''
            elif '-' not in rdf['predicate'] and len(rdf['predicate'].split()) == 1:
                rdf['predicate'] = lemmatize(cons[1]['raw'])
            '''

            if len(cons) > 2 and rdf['object'] == '':
                rdf['object'] = cons[2]['raw']

        print('RDF ', rdf)

        if len(rdf['subject'].split()) > 1:
            pos = rdf['subject'].split()[0]
            entry = find(pos.lower(), self.GRAMMAR, typ='pos')
            if entry and 'person' in entry and entry['person'] == 'first':
                rdf['predicate'] = rdf['subject'].split()[1] + '-is'
                rdf['subject'] = chat.speaker

        '''
        interpret_elements(cons)
        perspective = analyze_predicate(rdf['predicate'], self.GRAMMAR)

        if 'fix' in perspective:
            rdf['predicate'] = perspective['fix']
        self._perspective = perspective
        '''

        rdf = dereference_pronouns(self, rdf, self.GRAMMAR, self.chat.speaker)
        self._rdf = rdf

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


        #print(cons)


        # Main setting of things
        for key, elem in cons.items():
            if elem['label'].startswith('V'):
                if rdf['predicate'] and rdf['predicate'] != 'do':
                    rdf['object'] = elem['raw']
                else:
                    rdf['predicate'] = lemmatize(elem['raw'], 'v')

            elif 'structure' in elem:
                if elem['structure'].label().startswith('V'):
                    tree = elem['structure']
                    for branch in tree:
                        for node in branch:
                            if node.label()=='MD':
                                rdf['predicate'] = node.leaves()[0]
                            if node.label().startswith('V') and not find(node.leaves()[0], self.GRAMMAR, 'to_be'):
                                rdf['object'] = node.leaves()[0]

            if elem['label'] == 'PP':
                if 'structure' in elem:
                    tree = elem['structure']
                    for branch in tree:
                        for node in branch:
                            if node.label().startswith('N'):
                                rdf['subject'] = node.leaves()[0]
                            if node.label() == 'IN':
                                rdf['predicate']+='-'+node.leaves()[0]

            elif elem['label'] == 'NP':
                if key != len(cons) - 1:
                    rdf['subject'] = elem['raw']
                else:
                    rdf['object'] = elem['raw']

        print('initial ',rdf)

        # Fixes
        '''
        if find(rdf['object'], self.GRAMMAR, 'verb'):
            rdf['object'] = ''
            print(rdf)
        '''


        if find(rdf['predicate'], self.GRAMMAR, 'aux'):
            rdf['predicate'] = rdf['object']
            rdf['object'] = ''
            #print('fix ',rdf)

        if rdf['subject'] == '' and self.chat.last_utterance.tokens[0].lower() != 'who':
            if len(rdf['object'].split()) > 0:  # TODO revision by Lenka
                rdf['subject'] = rdf['object'].split()[0]
                rdf['predicate'] = 'be-' + rdf['object'].split()[1]
                rdf['object'] = ''

        if '-' in rdf['predicate'] and rdf['predicate'].split('-')[1] == 'from':
            rdf['predicate'] = 'be-from'


        #print('WHO-ANALYZER ', rdf)
        if cons[0]['raw'].lower() == 'who' and rdf['subject']!='':
            rdf['object'] = rdf['subject']
            rdf['subject'] = ''
            #rdf['object'] = cons[len(cons)-1]['raw'].lower()

            if '-' not in rdf['predicate']:
                rdf['predicate'] = lemmatize(cons[1]['raw'].lower(), 'v')

        if '-' not in rdf['predicate']:
            rdf['predicate'] = lemmatize(rdf['predicate'], 'v')



        #print('final ',rdf)
        rdf = dereference_pronouns(self, rdf, self.GRAMMAR, self.chat.speaker)
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
            polarity = -1
        word = lemmatize(word)
        entry = find(word, lexicon, 'verb')
        if entry:
            if 'sentiment' in entry:
                sent[word] = entry['sentiment']
            if 'certainty' in entry:
                cert[word] = entry['certainty']

    S = calculate_sentiment(sent) * polarity
    C = calculate_certainty(cert)
    perspective = {'sentiment': S, 'certainty': C, 'polarity': polarity}

    if polarity == -1:
        p = ''
        for word in predicate.split()[2:]:
            p += word + ' '
        p = p.strip()
        perspective['fix'] = p

    return perspective


def calculate_certainty(cert):
    C = 1
    for el in cert:
        C *= cert[el]
    return C


def calculate_sentiment(sent):
    if not len(sent):
        S = 0
    else:
        S = 1
        for el in sent:
            S *= sent[el]
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
            if cons[el]['label'].startswith('V') or cons[el]['label'] == 'MD':
                if rdf['predicate']:
                    if rdf['predicate'].lower() not in self.GRAMMAR['verbs']['auxiliaries']['to do']:
                        rdf['object'] = cons[el]['raw']
                    else:
                        rdf['predicate'] = cons[el]['raw']
                else:
                    rdf['predicate'] = cons[el]['raw']

            if 'structure' in cons[el]:
                tree = cons[el]['structure']

            if cons[el]['label'].startswith('N') or cons[el]['label'] == 'PRP':
                if rdf['subject']:
                    rdf['object'] = cons[el]['raw']
                else:
                    rdf['subject'] = cons[el]['raw']

        rdf = dereference_pronouns(self, rdf, self.GRAMMAR, self.chat.speaker)
        self._rdf = rdf

    @property
    def rdf(self):
        """
        Returns
        -------
        rdf: dict or None
        """
        return self._rdf


def interpret_elements(cons):
    for el in cons:
        # wordnet lookup
        if 'structure' in cons[el]:
            for word in cons[el]['raw'].split():
                label = get_node_label(cons[el]['structure'], word)
                syn = wu.get_synsets(word, label)
        else:
            word = cons[el]['raw']
            label = cons[el]['label']
            syn = wu.get_synsets(word, label)
        # TODO DBpedia lookup


def dbp_query(q, baseURL, format="application/json"):
    params = {
        "default-graph": "",
        "should-sponge": "soft",
        "query": q,
        "debug": "on",
        "timeout": "",
        "format": format,
        "save": "display",
        "fname": ""
    }
    querypart = urllib.urlencode(params)
    response = urllib.urlopen(baseURL, querypart).read()
    return json.loads(response)


def get_uri(string):
    query = """PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?pred WHERE {
  ?pred rdfs:label """ + "'" + string + "'" + """@en .
}
ORDER BY ?pred"""
    results = dbp_query(query, "http://dbpedia.org/sparql")
    uris = []
    for x in results['results']['bindings']:
        uris.append(x['pred']['value'])
    return uris


'''
import spacy
nlp = spacy.load('en')
sent = u'Vermeer is a famous painter from Delft.'
doc = nlp(sent)
for ent in doc.ents:
    uri = get_uri(ent.text)
    print(ent.text, ent.label_, uri)
'''

