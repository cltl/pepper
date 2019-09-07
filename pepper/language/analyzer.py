from .ner import NER
from .utils.helper_functions import *
from pepper.language.utils.atoms import UtteranceType


class Analyzer(object):
    # Load Grammar Json
    GRAMMAR_JSON = os.path.join(os.path.dirname(__file__), 'data', 'lexicon.json')
    with open(GRAMMAR_JSON) as json_file:
        LEXICON = json.load(json_file)

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
            Analyzer.LOG.warning("Couldn't parse input")
            return None

        for tree in forest:
            sentence_type = tree[0].label()

            if sentence_type == 'S':
                return StatementAnalyzer.analyze(chat)
            elif sentence_type == 'Q':
                return QuestionAnalyzer.analyze(chat)
            else:
                Analyzer.LOG.warning("Error: {}".format(sentence_type))

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
        return self._rdf

    @property
    def perspective(self):
        """
        Returns
        -------
        perspective: dict or None
        """

        return None

    def fix_predicate(self, predicate):

        # if predicate.endswith('-not'):
        #    predicate = predicate[:-4]

        if '-' not in predicate:
            predicate = lemmatize(predicate, 'v')

            if get_node_label(self.chat.last_utterance.parser.forest[0], predicate) in ['IN', 'TO']:
                predicate = 'be-' + predicate

            elif predicate == '':
                predicate = 'be'

        if predicate == 'hat':  # lemmatizer issue with verb 'hate'
            predicate = 'hate'

        elif predicate == 'bear':
            predicate = 'born'  # lemmatizer issue

        return predicate

    def analyze_vp(self, rdf, utterance_info):
        pred = ''
        ind = 0
        structure_tree = self.chat.last_utterance.parser.forest[0]

        if len(rdf['predicate'].split('-')) == 1:
            rdf['predicate'] = lemmatize(rdf['predicate'], 'v')

            if rdf['predicate'] == 'cannot':  # special case with no space between not and verb
                rdf['predicate'] = 'can'
                utterance_info['neg'] = True

            return rdf, utterance_info

        for el in rdf['predicate'].split('-'):
            label = get_node_label(structure_tree, el)

            if label == 'RB':
                if el in ['not', 'never', 'no']:
                    utterance_info['neg'] = True

            # verbs that carry sentiment or certainty are considered followed by their object
            elif lexicon_lookup(lemmatize(el, 'v'), 'lexical'):
                pred += '-' + lemmatize(el, 'v')
                for elem in rdf['predicate'].split('-')[ind + 1:]:
                    label = get_node_label(structure_tree, elem)
                    if label in ['TO', 'IN']:
                        pred += '-' + elem
                    else:
                        rdf['object'] = elem + '-' + rdf['object']
                rdf['predicate'] = pred
                break

            elif label in ['IN', 'TO']:
                pred += '-' + el
                for elem in rdf['predicate'].split('-')[ind + 1:]:
                    rdf['object'] = elem + '-' + rdf['object']
                rdf['predicate'] = pred
                break

            # auxiliary verb
            elif lexicon_lookup(el, 'aux'):  # and not rdf['predicate'].endswith('-is'):
                utterance_info['aux'] = lexicon_lookup(el, 'aux')

            # verb or modal verb
            elif label.startswith('V') or label in ['MD']:
                if pred == '':
                    pred = lemmatize(el, 'v')
                else:
                    pred += '-' + lemmatize(el, 'v')

            else:
                Analyzer.LOG.debug('uncaught verb phrase element {}:{}'.format(el, label))

            ind += 1

        if pred == '':
            pred = 'be'

        rdf['predicate'] = pred
        return rdf, utterance_info

    def analyze_np(self, rdf):
        # multi-word subject (posesive phrase)
        if len(rdf['subject'].split('-')) > 1:
            first_word = rdf['subject'].split('-')[0].lower()
            if lexicon_lookup(first_word) and 'person' in lexicon_lookup(first_word):
                rdf = self.analyze_possessive(rdf, 'subject')
        else:  # one word subject
            rdf['subject'] = fix_pronouns(rdf['subject'].lower(), self)
        return rdf

    def analyze_possessive(self, rdf, element):
        first_word = rdf[element].split('-')[0]
        subject = fix_pronouns(first_word, self)
        predicate = ''
        for word in rdf[element].split('-')[1:]:
            # words that express people are grouped together in the subject
            if (lexicon_lookup(word, 'kinship') or lexicon_lookup(lemmatize(word, 'n'), 'kinship')) or word == 'best':
                subject += '-' + word
            else:
                predicate += '-' + word

        if predicate:
            rdf['predicate'] = predicate + '-is'

        if element == 'object':
            rdf['object'] = rdf['subject']

        rdf['subject'] = subject

        return rdf

    @staticmethod
    def analyze_object_with_preposition(rdf):
        if lexicon_lookup(rdf['predicate'], 'aux') or lexicon_lookup(rdf['predicate'], 'modal'):
            rdf['predicate'] += '-be-' + rdf['object'].split('-')[0]
        else:
            rdf['predicate'] += '-' + rdf['object'].split('-')[0]
        rdf['object'] = rdf['object'].replace(rdf['object'].split('-')[0], '', 1)[1:]
        return rdf

    def analyze_one_word_object(self, rdf):
        structure_tree = self.chat.last_utterance.parser.forest[0]
        if lexicon_lookup(rdf['object']) and 'person' in lexicon_lookup(rdf['object']):
            if rdf['predicate'] == 'be':
                subject = fix_pronouns(rdf['object'].lower(), self)
                pred = ''
                for el in rdf['subject'].split('-')[1:]:
                    pred += el + '-'
                rdf['predicate'] = pred + 'is'
                rdf['object'] = rdf['subject'].split('-')[0]
                rdf['subject'] = subject
            else:
                rdf['object'] = fix_pronouns(rdf['object'].lower(), self)
        elif get_node_label(structure_tree, rdf['object']).startswith('V') and get_node_label(structure_tree,
                                                                                              rdf['predicate']) == 'MD':
            rdf['predicate'] += '-' + rdf['object']
            rdf['object'] = ''
        return rdf

    def get_types_in_rdf(self, rdf):
        # Get type
        for el in rdf:
            text = rdf[el]
            final_type = []
            rdf[el] = {'text': text, 'type': ''}

            # If no text was extracted we cannot get a type
            if text == '':
                continue

            # First attempt at typing via forest
            rdf[el]['type'] = get_type(text, self.chat.last_utterance.parser.forest[0])

            # Analyze types
            if type(rdf[el]['type']) == dict:
                # Loop through dictionary for multiword entities
                for typ in rdf[el]['type']:
                    # If type is None or empty, look it up
                    if rdf[el]['type'][typ] in [None, '']:
                        entry = lexicon_lookup(typ)

                        if entry is None:
                            if typ.lower() in ['leolani']:
                                final_type.append('robot')
                            elif typ.lower() in ['lenka', 'selene', 'suzana', 'bram', 'piek'] or typ.capitalize() == typ:
                                final_type.append('person')
                            else:
                                node = get_node_label(self.chat.last_utterance.parser.forest[0], typ)
                                if node in ['IN', 'TO']:
                                    final_type.append('preposition')
                                elif node.startswith('V'):
                                    final_type.append('verb')
                                elif node.startswith('N'):
                                    final_type.append('noun')

                        elif 'proximity' in entry:
                            final_type.append('deictic')
                        elif 'person' in entry:
                            final_type.append('pronoun')

                    else:
                        final_type.append(rdf[el]['type'][typ])
                rdf[el]['type'] = final_type

            # Patch special types
            elif rdf[el]['type'] in [None, '']:
                entry = lexicon_lookup(rdf[el]['text'])
                if entry is None:
                    if rdf[el]['text'].lower() in ['leolani']:
                        rdf[el]['type'] = ['robot']
                    if rdf[el]['text'].lower() in ['lenka', 'selene', 'suzana', 'bram', 'piek'] or typ.capitalize() == typ:
                        rdf[el]['type'] = ['person']
                elif 'proximity' in entry:
                    rdf[el]['type'] = ['deictic']

        return rdf


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
    def perspective(self):
        """
        Returns
        -------
        perspective: dict or None
        """
        raise NotImplementedError()


class GeneralStatementAnalyzer(StatementAnalyzer):
    @staticmethod
    def extract_perspective(predicate, utterance_info=None):
        sentiment = 0
        certainty = 1
        polarity = 1

        for word in predicate.split('-'):
            word = lemmatize(word)  # with a pos tag ?
            if word == 'not':
                utterance_info['neg'] = -1
            entry = lexicon_lookup(word, 'verb')
            if entry:
                if 'sentiment' in entry:
                    sentiment = entry['sentiment']
                if 'certainty' in entry:
                    certainty = entry['certainty']

        if 'certainty' in utterance_info:
            certainty = utterance_info['certainty']

        if utterance_info['neg']:
            polarity = -1

        perspective = {'sentiment': sentiment, 'certainty': certainty, 'polarity': polarity}
        return perspective

    @staticmethod
    def check_rdf_completeness(rdf):
        for el in ['predicate', 'subject', 'object']:
            if not rdf[el] or not len(rdf[el]):
                LOG.warning("Cannot find {} in statement".format(el))
                return False
        return True

    def analyze_certainty_statement(self, rdf):
        index = 0
        for subtree in self.chat.last_utterance.parser.constituents[2]['structure']:
            text = ''
            for leaf in subtree.leaves():
                if not (index == 0 and leaf == 'that'):
                    text += leaf + '-'
            if subtree.label() == 'VP':
                rdf['predicate'] = text[:-1]
            elif subtree.label() == 'NP':
                rdf['subject'] = text[:-1]
            else:
                rdf['object'] = text[:-1]
            index += 1
        return rdf

    def initialize_rdf(self):
        """
        assumed word order: NP VP C
        subject is the NP, predicate is VP and complement can be NP, VP, PP, another S or nothing

        """
        rdf = {'subject': self.chat.last_utterance.parser.constituents[0]['raw'],
               'predicate': self.chat.last_utterance.parser.constituents[1]['raw'],
               'object': self.chat.last_utterance.parser.constituents[2]['raw']}

        return rdf

    def analyze_multiword_object(self, rdf):
        structure_tree = self.chat.last_utterance.parser.forest[0]
        first_word = rdf['object'].split('-')[0]

        if get_node_label(structure_tree, first_word) in ['TO', 'IN']:
            rdf = self.analyze_object_with_preposition(rdf)

        if lexicon_lookup(first_word) and 'person' in lexicon_lookup(first_word):
            rdf = self.analyze_possessive(rdf, 'object')

        if get_node_label(structure_tree, first_word).startswith('V'):
            if get_node_label(structure_tree, rdf['predicate']) == 'MD':
                rdf['predicate'] += '-' + first_word
                rdf['object'] = rdf['object'].replace(first_word, '')

        return rdf

    def __init__(self, chat):
        """
        General Statement Analyzer

        Parameters
        ----------
        chat: Chat
            Chat to be analyzed
        """

        # Initialize
        super(GeneralStatementAnalyzer, self).__init__(chat)
        utterance_info = {'neg': False}
        rdf = self.initialize_rdf()
        Analyzer.LOG.debug('initial RDF: {}'.format(rdf))

        entry = lexicon_lookup(lemmatize(rdf['predicate'], 'v'), 'lexical')

        # sentences such as "I think (that) ..."
        if entry and 'certainty' in entry:
            if self.chat.last_utterance.parser.constituents[2]['label'] == 'S':
                utterance_info['certainty'] = entry['certainty']
                rdf = self.analyze_certainty_statement(rdf)

        rdf, utterance_info = self.analyze_vp(rdf, utterance_info)
        Analyzer.LOG.debug('after VP: {}'.format(rdf))

        rdf = self.analyze_np(rdf)
        Analyzer.LOG.debug('after NP: {}'.format(rdf))

        if len(rdf['object'].split('-')) > 1:  # multi-word object
            rdf = self.analyze_multiword_object(rdf)

        if len(rdf['object'].split('-')) == 1:
            rdf = self.analyze_one_word_object(rdf)

        # Final fixes to RDF
        rdf = trim_dash(rdf)
        rdf['predicate'] = self.fix_predicate(rdf['predicate'])
        self._perspective = self.extract_perspective(rdf['predicate'], utterance_info)
        rdf = self.get_types_in_rdf(rdf)
        Analyzer.LOG.debug('final RDF: {} {}'.format(rdf, utterance_info))
        self._rdf = rdf

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
            if first_word.lower() in Analyzer.LEXICON['question words']:
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


class WhQuestionAnalyzer(QuestionAnalyzer):

    def initialize_rdf(self):
        '''
        The assumed word order in wh-questions: aux before predicate, subject before object
        '''
        rdf = {'predicate': '', 'subject': '', 'object': ''}
        constituents = self.chat.last_utterance.parser.constituents
        if len(constituents) == 3:
            label = get_node_label(self.chat.last_utterance.parser.forest[0], constituents[2]['raw'])
            if constituents[0]['raw'] == 'who':
                rdf['predicate'] = constituents[1]['raw']
                rdf['object'] = constituents[2]['raw']
            elif label.startswith('V') or label == 'MD':  # rotation "(do you know) what a dog is?"s
                rdf['subject'] = constituents[1]['raw']
                rdf['predicate'] = constituents[2]['raw']
            else:
                rdf['predicate'] = constituents[1]['raw']
                rdf['subject'] = constituents[2]['raw']

        elif len(constituents) == 4:
            label = get_node_label(self.chat.last_utterance.parser.forest[0], constituents[1]['raw'])
            if not (label.startswith('V') or label == 'MD'):
                rdf['subject'] = constituents[3]['raw']
                rdf['predicate'] = constituents[2]['raw']
            else:
                rdf['subject'] = constituents[2]['raw']
                rdf['predicate'] = constituents[1]['raw'] + '-' + constituents[3]['raw']

        elif len(constituents) == 5:
            rdf['predicate'] = constituents[1]['raw'] + '-' + constituents[3]['raw']
            rdf['subject'] = constituents[2]['raw']
            rdf['object'] = constituents[4]['raw']
        else:
            Analyzer.LOG.debug('MORE CONSTITUENTS %s %s'.format(len(constituents), constituents))

        return rdf

    def analyze_multiword_object(self, rdf):
        first_word = rdf['object'].split('-')[0]

        if get_node_label(self.chat.last_utterance.parser.forest[0], first_word) in ['TO', 'IN']:
            rdf = self.analyze_object_with_preposition(rdf)

        if lexicon_lookup(first_word) and 'person' in lexicon_lookup(first_word):
            rdf = self.analyze_possessive(rdf, 'object')

        return rdf

    def __init__(self, chat):
        """
        Wh-Question Analyzer

        Parameters
        ----------
        chat: Chat
        """

        super(WhQuestionAnalyzer, self).__init__(chat)
        utterance_info = {'neg': False,
                          'wh_word': lexicon_lookup(self.chat.last_utterance.parser.constituents[0]['raw'].lower())}

        rdf = self.initialize_rdf()
        Analyzer.LOG.debug('initial RDF: {}'.format(rdf))

        rdf, utterance_info = self.analyze_vp(rdf, utterance_info)
        Analyzer.LOG.debug('after VP: {}'.format(rdf))

        rdf = self.analyze_np(rdf)
        Analyzer.LOG.debug('after NP: {}'.format(rdf))

        if len(rdf['object'].split('-')) > 1:  # multi-word object
            rdf = self.analyze_multiword_object(rdf)

        if len(rdf['object'].split('-')) == 1:
            rdf = self.analyze_one_word_object(rdf)

        # Final fixes to RDF
        rdf = trim_dash(rdf)
        rdf['predicate'] = self.fix_predicate(rdf['predicate'])
        rdf = self.get_types_in_rdf(rdf)
        Analyzer.LOG.debug('final RDF: {} {}'.format(rdf, utterance_info))
        self._rdf = rdf


# verb question rules:
class VerbQuestionAnalyzer(QuestionAnalyzer):

    def analyze_multiword_object(self, rdf):
        structure_tree = self.chat.last_utterance.parser.forest[0]
        first_word = rdf['object'].split('-')[0]
        if lexicon_lookup(first_word) and 'person' in lexicon_lookup(first_word):
            rdf = self.analyze_possessive(rdf, 'object')

        elif get_node_label(structure_tree, first_word) in ['IN', 'TO']:
            rdf = self.analyze_object_with_preposition(rdf)

        elif get_node_label(structure_tree, first_word).startswith('V') and get_node_label(structure_tree,
                                                                                           rdf['predicate']) == 'MD':
            for word in rdf['object'].split('-'):
                label = get_node_label(structure_tree, word)
                if label in ['IN', 'TO', 'MD'] or label.startswith('V'):
                    rdf['predicate'] += '-' + word
                    rdf['object'] = rdf['object'].replace(word, '')

        elif rdf['predicate'].endswith('-is'):
            rdf['predicate'] = rdf['predicate'][:-3]
            for word in rdf['object'].split('-')[:-1]:
                rdf['predicate'] += '-' + word
            rdf['object'] = rdf['object'].split('-')[len(rdf['object'].split('-')) - 1]
            rdf['predicate'] += '-is'

        return rdf

    def initialize_rdf(self):
        rdf = {'predicate': '', 'subject': '', 'object': ''}

        constituents = self.chat.last_utterance.parser.constituents
        rdf['subject'] = constituents[1]['raw']

        if len(constituents) == 4:
            rdf['predicate'] = constituents[0]['raw'] + '-' + constituents[2]['raw']
            rdf['object'] = constituents[3]['raw']
        elif len(constituents) == 3:
            rdf['predicate'] = constituents[0]['raw']
            rdf['object'] = constituents[2]['raw']
        else:
            Analyzer.LOG.debug('MORE CONSTITUENTS %s %s'.format(len(constituents), constituents))
        return rdf

    def __init__(self, chat):
        """
        Verb Question Analyzer

        Parameters
        ----------
        chat: Chat
        """

        # Initialize
        super(VerbQuestionAnalyzer, self).__init__(chat)
        utterance_info = {'neg': False}
        rdf = self.initialize_rdf()
        Analyzer.LOG.debug('initial RDF: {}'.format(rdf))

        rdf, utterance_info = self.analyze_vp(rdf, utterance_info)
        Analyzer.LOG.debug('after VP: {}'.format(rdf))

        if len(rdf['subject'].split('-')) > 1:
            first_word = rdf['subject'].split('-')[0].lower()
            if lexicon_lookup(first_word) and 'person' in lexicon_lookup(first_word):
                rdf = self.analyze_possessive(rdf, 'subject')

            if 'not-' in rdf['subject']:  # for sentences that start with negation "haven't you been to London?"
                rdf['subject'] = rdf['subject'].replace('not-', '')

        if len(rdf['subject'].split('-')) == 1:
            rdf['subject'] = fix_pronouns(rdf['subject'].lower(), self)

        Analyzer.LOG.debug('after NP: {}'.format(rdf))

        if len(rdf['object'].split('-')) > 1:  # multi-word object
            rdf = self.analyze_multiword_object(rdf)

        if len(rdf['object'].split('-')) == 1:
            rdf = self.analyze_one_word_object(rdf)

        # Final fixes to RDF
        rdf = trim_dash(rdf)
        rdf['predicate'] = self.fix_predicate(rdf['predicate'])
        rdf = self.get_types_in_rdf(rdf)
        Analyzer.LOG.debug('final RDF: {} {}'.format(rdf, utterance_info))
        self._rdf = rdf
