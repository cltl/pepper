from __future__ import unicode_literals

from pepper.language.pos import POS
from pepper.brain import Triple

from pepper import logger, config

from nltk import CFG, RecursiveDescentParser

from random import getrandbits
from datetime import datetime
import enum
import re
import os


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
        self._log = logger.getChild(self.__class__.__name__)

        self._tokens = self._clean(self._tokenize(transcript))

        self._parser = Parser(self)

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
        return self._parser

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
    CFG_GRAMMAR_FILE = os.path.join(os.path.dirname(__file__), 'data', 'cfg.txt')

    def __init__(self, utterance):

        if not Parser.POS_TAGGER:
            Parser.POS_TAGGER = POS()

        with open(Parser.CFG_GRAMMAR_FILE) as cfg_file:
            self._cfg = cfg_file.read()

        self._forest, self._constituents = self._parse(utterance)

    @property
    def forest(self):
        return self._forest

    @property
    def constituents(self):
        return self._constituents

    def _parse(self, utterance):
        tokenized_sentence = utterance.tokens
        pos = self.POS_TAGGER.tag(tokenized_sentence)
        print(pos)

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

        s_r = {} #syntactic_realizations
        index = 0

        forest = [tree for tree in parsed]

        if len(forest):
            for tree in forest[0]: #alternative trees? f
                for branch in tree:
                    for node in branch:
                        if type(node)== unicode or type(node)==str:
                            s_r[index] = {'label': branch.label()}
                            s_r[index]['raw'] = node

                        else:
                            #print('node label ',node.label())
                            s_r[index] = {'label': node.label()}
                            raw = ''
                            if len(node.leaves())>1:
                                for n in node.leaves():
                                    raw+=n+' '
                            else:
                                raw = node.leaves()

                            s_r[index]['raw'] = raw
                        index+=1

        return forest, s_r
