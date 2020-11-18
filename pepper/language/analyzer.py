from .ner import NER
from .utils.helper_functions import *
from pepper.language.utils.atoms import UtteranceType, Emotion, Time


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

            try:
                if sentence_type == 'S':
                    return StatementAnalyzer.analyze(chat)
                elif sentence_type == 'Q':
                    return QuestionAnalyzer.analyze(chat)
                else:
                    Analyzer.LOG.warning("Error: {}".format(sentence_type))

            except Exception:
                Analyzer.LOG.warning("Couldn't parse input")

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
    def triple(self):
        """
        Returns
        -------
        triple: dict or None
        """
        return self._triple

    @property
    def perspective(self):
        """
        Returns
        -------
        perspective: dict or None
        """

        return self._perspective

    def fix_predicate(self, predicate):
        """
        This function returns the lemmatized predicate and fixes the errors with lemmatizing
        :param predicate: predicate to lemmatize
        :return: lemmatized predicate
        """

        if '-' not in predicate:
            predicate = lemmatize(predicate, 'v')

            if get_pos_in_tree(self.chat.last_utterance.parser.forest[0], predicate) in ['IN', 'TO']:
                predicate = 'be-' + predicate

            elif predicate == '':
                predicate = 'be'

        if predicate == 'hat':  # lemmatizer issue with verb 'hate'
            predicate = 'hate'

        elif predicate == 'bear':  # bear-in
            predicate = 'born'  # lemmatizer issue

        return predicate

    def analyze_vp(self, triple, utterance_info):
        """
        This function analyzes verb phrases
        :param triple: triple (subject, predicate, complement)
        :param utterance_info: the result of analysis thus far
        :return: triple and utterance info, updated with the results of VP analysis
        """
        pred = ''
        ind = 0
        structure_tree = self.chat.last_utterance.parser.forest[0]

        # one word predicate is just lemmatized
        if len(triple['predicate'].split('-')) == 1:
            triple['predicate'] = lemmatize(triple['predicate'], 'v')

            if triple['predicate'] == 'cannot':  # special case with no space between not and verb
                triple['predicate'] = 'can'
                utterance_info['neg'] = True

            return triple, utterance_info

        # complex predicate
        for el in triple['predicate'].split('-'):
            label = get_pos_in_tree(structure_tree, el)

            # negation
            if label == 'RB':
                if el in ['not', 'never', 'no']:
                    utterance_info['neg'] = True

            # verbs that carry sentiment or certainty are considered followed by their object
            elif lexicon_lookup(lemmatize(el, 'v'), 'lexical'):
                pred += '-' + lemmatize(el, 'v')
                for elem in triple['predicate'].split('-')[ind + 1:]:
                    label = get_pos_in_tree(structure_tree, elem)
                    if label in ['TO', 'IN']:
                        pred += '-' + elem
                    else:
                        triple['complement'] = elem + '-' + triple['complement']
                triple['predicate'] = pred
                break

            # prepositions are joined to the predicate and removed from the complement
            elif label in ['IN', 'TO']:
                pred += '-' + el
                for elem in triple['predicate'].split('-')[ind + 1:]:
                    triple['complement'] = elem + '-' + triple['complement']
                triple['predicate'] = pred
                break

            # auxiliary verb
            elif lexicon_lookup(el, 'aux'):  # and not triple['predicate'].endswith('-is'):
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

        triple['predicate'] = pred
        return triple, utterance_info

    def analyze_np(self, triple):
        """
        This function analyses noun phrases
        :param triple: S,P,C triple
        :return: triple with updated elements
        """

        # multi-word subject (possessive phrase)
        if len(triple['subject'].split('-')) > 1:
            first_word = triple['subject'].split('-')[0].lower()
            if lexicon_lookup(first_word) and 'person' in lexicon_lookup(first_word):
                triple = self.analyze_possessive(triple, 'subject')
            # TODO else

        else:  # one word subject
            triple['subject'] = fix_pronouns(triple['subject'].lower(), self)
        return triple

    def analyze_possessive(self, triple, element):
        """
        This function analyses possessive phrases, which start with pos. pronoun
        :param triple: subject, predicate, complement triple
        :param element: element of the triple which has the possessive phrase
        :return: updated triple
        """
        first_word = triple[element].split('-')[0]

        if element == 'complement':
            complement = fix_pronouns(first_word, self)

            for word in triple['complement'].split('-')[1:]:
                complement += '-' + word

            triple['complement'] = complement

        else:

            subject = fix_pronouns(first_word, self)
            predicate = ''
            for word in triple[element].split('-')[1:]:
                # words that express people are grouped together in the subject
                if (lexicon_lookup(word, 'kinship') or lexicon_lookup(lemmatize(word, 'n'),
                                                                      'kinship')) or word == 'best':
                    subject += '-' + word
                else:
                    predicate += '-' + word
            if element == 'complement':
                triple['complement'] = triple['subject']

            # properties are stored with a suffix "-is"
            if predicate:
                triple['predicate'] = predicate + '-is'

            triple['subject'] = subject

        return triple

    @staticmethod
    def analyze_complement_with_preposition(triple):
        """
        This function analyses triple complement which starts with a preposition and updates the triple
        :param triple: S,P,C triple
        :return: updated triple
        """
        if lexicon_lookup(triple['predicate'], 'aux') or lexicon_lookup(triple['predicate'], 'modal'):
            triple['predicate'] += '-be-' + triple['complement'].split('-')[0]
        else:
            triple['predicate'] += '-' + triple['complement'].split('-')[0]
        triple['complement'] = triple['complement'].replace(triple['complement'].split('-')[0], '', 1)[1:]
        return triple

    def analyze_one_word_complement(self, triple):
        """
        This function analyses one word complement and updates the triple
        :param triple: S,P,C triple
        :return: updated triple
        """
        structure_tree = self.chat.last_utterance.parser.forest[0]

        # TODO
        if lexicon_lookup(triple['complement']) and 'person' in lexicon_lookup(triple['complement']):
            if triple['predicate'] == 'be':
                subject = fix_pronouns(triple['complement'].lower(), self)
                pred = ''
                for el in triple['subject'].split('-')[1:]:
                    pred += el + '-'
                triple['predicate'] = pred + 'is'
                triple['complement'] = triple['subject'].split('-')[0]
                triple['subject'] = subject
            else:
                triple['complement'] = fix_pronouns(triple['complement'].lower(), self)
        elif get_pos_in_tree(structure_tree, triple['complement']).startswith('V') and get_pos_in_tree(
                structure_tree,
                triple[
                    'predicate']) == 'MD':
            triple['predicate'] += '-' + triple['complement']
            triple['complement'] = ''
        return triple

    def get_types_in_triple(self, triple):
        """
        This function gets types for all the elements of the triple
        :param triple: S,P,C triple
        :return: triple dictionary with types
        """
        # Get type
        for el in triple:
            text = triple[el]
            final_type = []
            triple[el] = {'text': text, 'type': []}

            # If no text was extracted we cannot get a type
            if text == '':
                continue

            # First attempt at typing via forest
            triple[el]['type'] = get_triple_element_type(text, self.chat.last_utterance.parser.forest[0])

            # Analyze types
            if type(triple[el]['type']) == dict:
                # Loop through dictionary for multiword entities
                for typ in triple[el]['type']:
                    # If type is None or empty, look it up
                    if triple[el]['type'][typ] in [None, '']:
                        entry = lexicon_lookup(typ)

                        if entry is None:
                            if typ.lower() in ['leolani']:
                                final_type.append('robot')
                            elif typ.lower() in ['lenka', 'selene', 'suzana', 'bram',
                                                 'piek'] or typ.capitalize() == typ:
                                final_type.append('person')
                            else:
                                node = get_pos_in_tree(self.chat.last_utterance.parser.forest[0], typ)
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
                        final_type.append(triple[el]['type'][typ])
                triple[el]['type'] = final_type

            # Patch special types
            elif triple[el]['type'] in [None, '']:
                entry = lexicon_lookup(triple[el]['text'])
                if entry is None:

                    # TODO: Remove Hardcoded Names
                    if triple[el]['text'].lower() in ['leolani']:
                        triple[el]['type'] = ['robot']
                    elif triple[el]['text'].lower() in ['lenka', 'selene', 'suzana', 'bram', 'piek']:
                        triple[el]['type'] = ['person']
                    elif triple[el]['text'].capitalize() == triple[el]['text']:
                        triple[el]['type'] = ['person']
                elif 'proximity' in entry:
                    triple[el]['type'] = ['deictic']

        return triple


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
    def triple(self):
        """
        Returns
        -------
        triple: dict or None
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
    @staticmethod
    def extract_perspective(predicate, utterance_info=None):
        """
        This function extracts perspective from statements
        :param predicate: statement predicate
        :param utterance_info: product of statement analysis thus far
        :return: perspective dictionary consisting of sentiment, certainty, and polarity value
        """
        sentiment = 0
        certainty = 1
        polarity = 1
        emotion = Emotion.NEUTRAL

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

        perspective = {'sentiment': sentiment, 'certainty': certainty, 'polarity': polarity, 'emotion': emotion}
        return perspective

    @staticmethod
    def check_triple_completeness(triple):
        """
        This function checks whether an extracted triple is complete
        :param triple: S,P,C triple
        :return: True if the triple has all three elements, False otherwise
        """
        for el in ['predicate', 'subject', 'complement']:
            if not triple[el] or not len(triple[el]):
                LOG.warning("Cannot find {} in statement".format(el))
                return False
        return True

    @staticmethod
    def check_perspective_completeness(perspective):
        """
        This function checks whether an extracted perspective is complete
        :param perspective: sentiment, certainty, polarity, emotion perspective
        :return: True if the perspective has all four elements, False otherwise
        """
        for el in ['sentiment', 'certainty', 'polarity', 'emotion']:
            if not perspective[el] or not len(perspective[el]):
                LOG.warning("Cannot find {} in statement".format(el))
                return False
        return True

    def analyze_certainty_statement(self, triple):
        """

        :param triple:
        :return:
        """
        index = 0
        for subtree in self.chat.last_utterance.parser.constituents[2]['structure']:
            text = ''
            for leaf in subtree.leaves():
                if not (index == 0 and leaf == 'that'):
                    text += leaf + '-'
            if subtree.label() == 'VP':
                triple['predicate'] = text[:-1]
            elif subtree.label() == 'NP':
                triple['subject'] = text[:-1]
            else:
                triple['complement'] = text[:-1]
            index += 1
        return triple

    def initialize_triple(self):
        """
        This function initializes the triple with assumed word order: NP VP C
        subject is the NP, predicate is VP and complement can be NP, VP, PP, another S or nothing
        """

        triple = {'subject': self.chat.last_utterance.parser.constituents[0]['raw'],
                  'predicate': self.chat.last_utterance.parser.constituents[1]['raw'],
                  'complement': self.chat.last_utterance.parser.constituents[2]['raw']}

        return triple

    def analyze_multiword_complement(self, triple):
        """
        This function analyses complex complements in statements
        :param triple: S,P,C triple
        :return: updated triple
        """
        structure_tree = self.chat.last_utterance.parser.forest[0]
        first_word = triple['complement'].split('-')[0]

        if get_pos_in_tree(structure_tree, first_word) in ['TO', 'IN']:
            triple = self.analyze_complement_with_preposition(triple)

        if lexicon_lookup(first_word) and 'person' in lexicon_lookup(first_word):
            triple = self.analyze_possessive(triple, 'complement')

        if get_pos_in_tree(structure_tree, first_word).startswith('V'):
            if get_pos_in_tree(structure_tree, triple['predicate']) == 'MD':
                triple['predicate'] += '-' + first_word
                triple['complement'] = triple['complement'].replace(first_word, '')

        return triple

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

        # Initial parsing
        triple = self.initialize_triple()
        Analyzer.LOG.debug('initial triple: {}'.format(triple))

        # sentences such as "I think (that) ..."
        entry = lexicon_lookup(lemmatize(triple['predicate'], 'v'), 'lexical')
        if entry and 'certainty' in entry:
            if self.chat.last_utterance.parser.constituents[2]['label'] == 'S':
                utterance_info['certainty'] = entry['certainty']
                triple = self.analyze_certainty_statement(triple)

        # Analyze verb phrase
        triple, utterance_info = self.analyze_vp(triple, utterance_info)
        Analyzer.LOG.debug('after VP: {}'.format(triple))

        # Analyze noun phrase
        triple = self.analyze_np(triple)
        Analyzer.LOG.debug('after NP: {}'.format(triple))

        # Analyze complement
        if len(triple['complement'].split('-')) > 1:  # multi-word complement
            triple = self.analyze_multiword_complement(triple)
        elif len(triple['complement'].split('-')) == 1:
            triple = self.analyze_one_word_complement(triple)
        Analyzer.LOG.debug('after complement analysis: {}'.format(triple))

        # Final fixes to triple
        triple = trim_dash(triple)
        triple['predicate'] = self.fix_predicate(triple['predicate'])
        Analyzer.LOG.debug('after predicate fix: {}'.format(triple))

        # Extract perspective
        self._perspective = self.extract_perspective(triple['predicate'], utterance_info)
        Analyzer.LOG.info('extracted perspective: {}'.format(self._perspective))

        # Get types
        triple = self.get_types_in_triple(triple)
        Analyzer.LOG.debug('final triple: {} {}'.format(triple, utterance_info))

        # Final triple assignment
        self._triple = triple

    @property
    def triple(self):
        """
        Returns
        -------
        triple: dict or None
        """
        return self._triple

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

        # TODO: Implement Chat -> triple

        self._triple = {}

    @property
    def triple(self):
        """
        Returns
        -------
        triple: dict or None
        """
        return self._triple


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

    @property
    def triple(self):
        """
        Returns
        -------
        triple: dict or None
        """
        raise NotImplementedError()


class WhQuestionAnalyzer(QuestionAnalyzer):

    def initialize_triple(self):
        """
        This function initializes the triple for wh_questions with the assumed word order: aux before predicate, subject before complement
        :return: initial S,P,C triple
        """

        triple = {'predicate': '', 'subject': '', 'complement': ''}
        constituents = self.chat.last_utterance.parser.constituents
        if len(constituents) == 3:
            label = get_pos_in_tree(self.chat.last_utterance.parser.forest[0], constituents[2]['raw'])
            if constituents[0]['raw'] == 'who':
                triple['predicate'] = constituents[1]['raw']
                triple['complement'] = constituents[2]['raw']
            elif label.startswith('V') or label == 'MD':  # rotation "(do you know) what a dog is?"s
                triple['subject'] = constituents[1]['raw']
                triple['predicate'] = constituents[2]['raw']
            else:
                triple['predicate'] = constituents[1]['raw']
                triple['subject'] = constituents[2]['raw']

        elif len(constituents) == 4:
            label = get_pos_in_tree(self.chat.last_utterance.parser.forest[0], constituents[1]['raw'])
            if not (label.startswith('V') or label == 'MD'):
                triple['subject'] = constituents[3]['raw']
                triple['predicate'] = constituents[2]['raw']
            else:
                triple['subject'] = constituents[2]['raw']
                triple['predicate'] = constituents[1]['raw'] + '-' + constituents[3]['raw']

        elif len(constituents) == 5:
            triple['predicate'] = constituents[1]['raw'] + '-' + constituents[3]['raw']
            triple['subject'] = constituents[2]['raw']
            triple['complement'] = constituents[4]['raw']
        else:
            Analyzer.LOG.debug('MORE CONSTITUENTS %s %s'.format(len(constituents), constituents))

        return triple

    def analyze_multiword_complement(self, triple):
        first_word = triple['complement'].split('-')[0]

        if get_pos_in_tree(self.chat.last_utterance.parser.forest[0], first_word) in ['TO', 'IN']:
            triple = self.analyze_complement_with_preposition(triple)

        if lexicon_lookup(first_word) and 'person' in lexicon_lookup(first_word):
            triple = self.analyze_possessive(triple, 'complement')

        return triple

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

        triple = self.initialize_triple()
        Analyzer.LOG.debug('initial triple: {}'.format(triple))

        triple, utterance_info = self.analyze_vp(triple, utterance_info)
        Analyzer.LOG.debug('after VP: {}'.format(triple))

        triple = self.analyze_np(triple)
        Analyzer.LOG.debug('after NP: {}'.format(triple))

        if len(triple['complement'].split('-')) > 1:  # multi-word complement
            triple = self.analyze_multiword_complement(triple)

        if len(triple['complement'].split('-')) == 1:
            triple = self.analyze_one_word_complement(triple)

        # Final fixes to triple
        triple = trim_dash(triple)
        triple['predicate'] = self.fix_predicate(triple['predicate'])
        triple = self.get_types_in_triple(triple)
        Analyzer.LOG.debug('final triple: {} {}'.format(triple, utterance_info))
        self._triple = triple

    @property
    def triple(self):
        """
        Returns
        -------
        triple: dict or None
        """
        return self._triple


class VerbQuestionAnalyzer(QuestionAnalyzer):

    def analyze_multiword_complement(self, triple):
        structure_tree = self.chat.last_utterance.parser.forest[0]
        first_word = triple['complement'].split('-')[0]
        if lexicon_lookup(first_word) and 'person' in lexicon_lookup(first_word):
            triple = self.analyze_possessive(triple, 'complement')

        elif get_pos_in_tree(structure_tree, first_word) in ['IN', 'TO']:
            triple = self.analyze_complement_with_preposition(triple)

        elif get_pos_in_tree(structure_tree, first_word).startswith('V') and get_pos_in_tree(structure_tree,
                                                                                             triple[
                                                                                                 'predicate']) == 'MD':
            for word in triple['complement'].split('-'):
                label = get_pos_in_tree(structure_tree, word)
                if label in ['IN', 'TO', 'MD'] or label.startswith('V'):
                    triple['predicate'] += '-' + word
                    triple['complement'] = triple['complement'].replace(word, '')

        elif triple['predicate'].endswith('-is'):
            triple['predicate'] = triple['predicate'][:-3]
            for word in triple['complement'].split('-')[:-1]:
                triple['predicate'] += '-' + word
            triple['complement'] = triple['complement'].split('-')[len(triple['complement'].split('-')) - 1]
            triple['predicate'] += '-is'

        return triple

    def initialize_triple(self):
        triple = {'predicate': '', 'subject': '', 'complement': ''}

        constituents = self.chat.last_utterance.parser.constituents
        triple['subject'] = constituents[1]['raw']

        if len(constituents) == 4:
            triple['predicate'] = constituents[0]['raw'] + '-' + constituents[2]['raw']
            triple['complement'] = constituents[3]['raw']
        elif len(constituents) == 3:
            triple['predicate'] = constituents[0]['raw']
            triple['complement'] = constituents[2]['raw']
        else:
            Analyzer.LOG.debug('MORE CONSTITUENTS %s %s'.format(len(constituents), constituents))
        return triple

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
        triple = self.initialize_triple()
        Analyzer.LOG.debug('initial triple: {}'.format(triple))

        triple, utterance_info = self.analyze_vp(triple, utterance_info)
        Analyzer.LOG.debug('after VP: {}'.format(triple))

        if len(triple['subject'].split('-')) > 1:
            first_word = triple['subject'].split('-')[0].lower()
            if lexicon_lookup(first_word) and 'person' in lexicon_lookup(first_word):
                triple = self.analyze_possessive(triple, 'subject')

            if 'not-' in triple['subject']:  # for sentences that start with negation "haven't you been to London?"
                triple['subject'] = triple['subject'].replace('not-', '')

        if len(triple['subject'].split('-')) == 1:
            triple['subject'] = fix_pronouns(triple['subject'].lower(), self)

        Analyzer.LOG.debug('after NP: {}'.format(triple))

        if len(triple['complement'].split('-')) > 1:  # multi-word complement
            triple = self.analyze_multiword_complement(triple)

        if len(triple['complement'].split('-')) == 1:
            triple = self.analyze_one_word_complement(triple)

        # Final fixes to triple
        triple = trim_dash(triple)
        triple['predicate'] = self.fix_predicate(triple['predicate'])
        triple = self.get_types_in_triple(triple)
        Analyzer.LOG.debug('final triple: {} {}'.format(triple, utterance_info))
        self._triple = triple

    @property
    def triple(self):
        """
        Returns
        -------
        triple: dict with S,P,C or None
        """
        return self._triple
