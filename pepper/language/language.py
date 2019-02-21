from __future__ import unicode_literals

from pepper.language.ner import NER
from pepper.language.pos import POS
from pepper import logger
from pepper import config

from pepper.brain import LongTermMemory, Triple
import pepper.brain.utils.helper_functions as brain_help

from nltk import CFG, RecursiveDescentParser

from random import getrandbits
from datetime import datetime
import enum
import json
import re
import os
import utils


class UtteranceType(enum.Enum):
    STATEMENT = 0
    QUESTION = 1
    EXPERIENCE = 2  # TODO


class Certainty(enum.Enum):
    CERTAIN = 0
    PROBABLE = 1
    POSSIBLE = 2
    UNDERSPECIFIED = 3


class Sentiment(enum.Enum):
    NEGATIVE = 0
    POSITIVE = 1


class Emotion(enum.Enum):
    ANGER = 0
    DISGUST = 1
    FEAR = 2
    HAPPINESS = 3
    SADNESS = 4
    SURPRISE = 5


class Chat(object):
    def __init__(self, speaker, context):
        """
        Create Chat

        Parameters
        ----------
        speaker: str
            Name of speaker (a.k.a. the person Pepper has a chat with)
        """

        self._id = getrandbits(128)
        self._context = context
        self._speaker = speaker
        self._utterances = []

        self._log = logger.getChild("{} ({})".format(self.__class__.__name__, self.speaker))

    @property
    def context(self):
        """
        Returns
        -------
        context: Context
            Context
        """
        return self._context

    @property
    def speaker(self):
        """
        Returns
        -------
        speaker: str
            Name of speaker (a.k.a. the person Pepper has a chat with)
        """
        return self._speaker

    @property
    def id(self):
        """
        Returns
        -------
        id: int
            Unique (random) identifier of this chat
        """
        return self._id

    @property
    def utterances(self):
        """
        Returns
        -------
        utterances: list of Utterance
            List of utterances that occurred in this chat
        """
        return self._utterances

    @property
    def last_utterance(self):
        """
        Returns
        -------
        last_utterance: Utterance
            Most recent Utterance
        """
        return self._utterances[-1]

    def add_utterance(self, text, me):
        """
        Add Utterance to Conversation

        Parameters
        ----------
        text: str
            Utterance Text to add to conversation

        Returns
        -------
        utterance: Utterance
        """
        utterance = Utterance(self, text, me, len(self._utterances))
        self._log.info(utterance)
        self._utterances.append(utterance)
        return utterance

    def __repr__(self):
        return "\n".join([str(utterance) for utterance in self._utterances])


class Utterance(object):
    def __init__(self, chat, transcript, me, turn):
        """
        Construct Utterance Object

        Parameters
        ----------
        chat: Chat
            Reference to Chat Utterance is part of
        transcript: str
            Uttered text (Natural Language)
        me: bool
            True if Robot spoke, False if Person Spoke
        turn: int
            Utterance Turn
        """

        self._chat = chat
        self._transcript = transcript
        self._me = me
        self._turn = turn
        self._datetime = datetime.now()

        self._tokens = self._clean(self._tokenize(transcript))
        self._parsed_tree = Parser().parse(self)

    @property
    def chat(self):
        """
        Returns
        -------
        chat: Chat
            Utterance Chat
        """
        return self._chat

    @property
    def type(self):
        # type: () -> UtteranceType
        raise NotImplementedError()

    @property
    def transcript(self):
        """
        Returns
        -------
        transcript: str
            Utterance Transcript
        """
        return self._transcript

    @property
    def me(self):
        # type: () -> bool
        """
        Returns
        -------
        me: bool
            True if Robot spoke, False if Person Spoke
        """
        return self._me

    @property
    def turn(self):
        # type: () -> int
        """
        Returns
        -------
        turn: int
            Utterance Turn
        """
        return self._turn

    @property
    def triple(self):
        # type: () -> Triple
        raise NotImplementedError()

    @property
    def datetime(self):
        return self._datetime

    @property
    def language(self):
        """
        Returns
        -------
        language: str
            Original language of the Transcript
        """
        raise NotImplementedError()

    @property
    def certainty(self):
        # type: () -> Certainty
        raise NotImplementedError()

    @property
    def sentiment(self):
        # type: () -> Sentiment
        raise NotImplementedError()

    @property
    def emotion(self):
        # type: () -> Emotion
        raise NotImplementedError()

    @property
    def tokens(self):
        """
        Returns
        -------
        tokens: list of str
            Tokenized transcript
        """
        return self._tokens

    @property
    def parsed_tree(self):
        """
        Returns
        -------
        parsed_tree: ntlk Tree generated by the CFG parser
        """
        return self._parsed_tree

    def _tokenize(self, transcript):
        """
        Parameters
        ----------
        transcript: str
            Uttered text (Natural Language)

        Returns
        -------
        tokens: list of str
            Tokenized transcript: list of cleaned tokens
                - remove contractions
        """

        tokens_raw = transcript.split()
        tokens = []
        for word in tokens_raw:
            clean_word = re.sub('[?!]', '', word)
            tokens.append(clean_word)
        return tokens

    def _clean(self, tokens):
        """
        Parameters
        ----------
        tokens: list of str
            Tokenized transcript

        Returns
        -------
        cleaned_tokens: list of str
            Tokenized & Cleaned transcript
        """

        # TODO: Remove Contractions

        return tokens

    def __repr__(self):
        author = config.NAME if self.me else self.chat.speaker
        return "Utterance {:03d}: {:10s} -> {}".format(self.turn, author, self.transcript)


class Parser(object):

    POS_TAGGER = None  # Type: POS
    CFG_GRAMMAR_FILE = os.path.join(os.path.dirname(__file__), 'cfg.txt')

    def __init__(self):
        if not Parser.POS_TAGGER:
            Parser.POS_TAGGER = POS()

        with open(Parser.CFG_GRAMMAR_FILE) as cfg_file:
            self._cfg = cfg_file.read()

    def parse(self, utterance):
        tokenized_sentence = utterance.tokens
        pos = self.POS_TAGGER.tag(tokenized_sentence)
        #print(pos)

        '''
        doc = nlp(utterance.transcript)
        for token in doc:
            #print(token.text, token.lemma_, token.pos_)
            ind = 0
            for w in pos:
                if w[0]==token.text and w[1]!=token.pos_:
                    print('mismatch ',w[1],token.pos_)
                    if w[1]=='IN' and token.pos_=='VERB':
                        pos[ind]=(token.text,'VBP')
                ind+=1
        '''

        ind = 0
        for w in tokenized_sentence:
            if w=='like':
                pos[ind] = (w, 'VBP')
            ind+=1


        for el in pos:
            if el[1].endswith('$'):
                new_rule = el[1][:-1] + 'POS -> \'' + el[0] + '\'\n'
            else:
                new_rule = el[1] + ' -> \'' + el[0] + '\'\n'
            if new_rule not in self._cfg:
                self._cfg += new_rule

        cfg_parser = CFG.fromstring(self._cfg)
        RD = RecursiveDescentParser(cfg_parser)
        parsed = RD.parse(tokenized_sentence)
        return [tree for tree in parsed]


class Analyzer(object):

    # Load Grammar Json
    GRAMMAR_JSON = os.path.join(os.path.dirname(__file__), 'grammar.json')
    with open(GRAMMAR_JSON) as json_file:
        GRAMMAR = json.load(json_file)['grammar']

    # Load Stanford Named Entity Recognition Server
    NER = None  # type: NER

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
        self._log = logger.getChild(self.__class__.__name__)

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

        forest = chat.last_utterance.parsed_tree

        if not forest:
            print("unparsed input")
            #raise Exception("Ungrammatical Input") #TODO

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
    def log(self):
        """
        Returns
        -------
        log: logging.Logger
        """
        return self._log

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

        super(GeneralStatementAnalyzer, self).__init__(chat)

        rdf = {'predicate': '', 'subject': '', 'object': ''}
        position = 0
        dict = {}

        for tree in chat.last_utterance.parsed_tree[0]:
            for branch in tree:
                for node in branch:

                    if len(node.leaves())>1:
                        for n in node.leaves():
                            print ('n ', n)

                    position += 1

                    #print(node.label(), node.leaves()[0])
                    if node.label().startswith('V') and \
                            (node.leaves()[0].lower() in self.GRAMMAR['verbs'] or node.leaves()[0].lower()[:-1] in
                                self.GRAMMAR['verbs'] or node.leaves()[0].lower() in self.GRAMMAR['to be']):
                        rdf['predicate'] += node.leaves()[0] + ' '

                    elif node.leaves()[0]=='from':
                        if rdf['predicate'].strip() in self.GRAMMAR['to be']:
                            rdf['predicate'] = 'is_from'

                    elif node.leaves()[0].lower() in self.GRAMMAR['pronouns'] and position < len(
                            chat.last_utterance.tokens):
                        rdf['subject'] += node.leaves()[0] + ' '
                        dict['pronoun'] = self.GRAMMAR['pronouns'][node.leaves()[0].lower()]
                        rdf['subject'] = utils.fix_pronouns(dict, self.chat.speaker)

                    elif node.label().startswith('N') and position == len(chat.last_utterance.tokens):
                        rdf['object'] += node.leaves()[0] + ' '




        for el in rdf:
            rdf[el] = rdf[el].strip()

        if rdf['object'].lower() in self.GRAMMAR['pronouns']:
            dict['pronoun'] = self.GRAMMAR['pronouns'][node.leaves()[0].lower()]
            rdf['object'] = utils.fix_pronouns(dict, self.chat.speaker)

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
        position = 0
        dict = {}

        for tree in chat.last_utterance.parsed_tree[0]:
            for branch in tree:
                for node in branch:
                    for leaf in node.leaves():

                        position += 1
                        #print(node.label(), leaf)

                        if node.label().startswith('V') and \
                                (leaf.lower() in self.GRAMMAR['verbs'] or leaf.lower()[:-1]in self.GRAMMAR['verbs']):
                            rdf['predicate'] += leaf + ' '

                        elif leaf.lower() in self.GRAMMAR['pronouns'] and position < len(chat.last_utterance.tokens):
                            rdf['subject'] += leaf + ' '
                            dict['pronoun'] = self.GRAMMAR['pronouns'][leaf.lower()]

                        elif node.label().startswith('N') and position == len(chat.last_utterance.tokens):
                            rdf['object'] += leaf + ' '

                        elif leaf.lower()=='from':
                            rdf['predicate']='is_from'

        for el in rdf:
            rdf[el] = rdf[el].strip()

        if 'pronoun' in dict:
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


class VerbQuestionAnalyzer(QuestionAnalyzer):
    def __init__(self, chat):
        """
        Verb Question Analyzer

        Parameters
        ----------
        chat: Chat
        """

        super(VerbQuestionAnalyzer, self).__init__(chat)

        rdf = {'predicate': '', 'subject':'', 'object':''}
        position = 0
        dict = {}

        for tree in chat.last_utterance.parsed_tree[0]:
            for branch in tree:
                for node in branch:
                    position += 1
                    #print(node.label(), node.leaves()[0])
                    if node.label().startswith('V') and node.leaves()[0].lower() in self.GRAMMAR['verbs']:
                        rdf['predicate']+=node.leaves()[0]+' '

                    elif node.leaves()[0].lower() in self.GRAMMAR['pronouns'] and position<len(chat.last_utterance.tokens):
                        rdf['subject']+=node.leaves()[0]+' '
                        dict['pronoun'] = self.GRAMMAR['pronouns'][node.leaves()[0].lower()]

                    elif node.label().startswith('N') and position==len(chat.last_utterance.tokens):
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




def analyze(chat, brain):

    analyzer = Analyzer.analyze(chat)


    if analyzer.rdf['predicate'] in analyzer.GRAMMAR['verbs']:
        analyzer.rdf['predicate']+='s'

    if analyzer.utterance_type == UtteranceType.STATEMENT:
        if not utils.check_rdf_completeness(analyzer.rdf):
            print('incomplete statement RDF')
            return


    template = utils.write_template(chat.speaker, analyzer.rdf, chat.id, chat.last_utterance.chat_turn,
                                    analyzer.utterance_type)
    print(template)

    return chat.last_utterance




#"where are you from", "you know me", "do you know me","I am from China"
def test():
    utterances = ["I am from Belgrade"]
    chat = Chat("Lenka", None)
    brain = LongTermMemory()
    for utterance in utterances:
        brain_response = get_response(chat, utterance, brain)
        print('\n\n')
    return

#if __name__ == "__main__":
#    test()

