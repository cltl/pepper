from __future__ import unicode_literals

from pepper.language.pos import POS
from pepper.brain import Triple

from pepper import logger, config

from nltk import CFG, RecursiveDescentParser, edit_distance

from collections import Counter

from random import getrandbits
from datetime import datetime
import enum
import os

from typing import List, Optional


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
        context: Context
            Context Chat is part of
        """

        self._id = getrandbits(128)
        self._context = context
        self._speaker = speaker
        self._utterances = []

        self._log = self._update_logger()
        self._log.info("<< Start of Chat with {} >>".format(speaker))

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
        # type: () -> str
        """
        Returns
        -------
        speaker: str
            Name of speaker (a.k.a. the person Pepper has a chat with)
        """
        return self._speaker

    @speaker.setter
    def speaker(self, value):
        self._speaker = value

    @property
    def id(self):
        # type: () -> int
        """
        Returns
        -------
        id: int
            Unique (random) identifier of this chat
        """
        return self._id

    @property
    def utterances(self):
        # type: () -> List[Utterance]
        """
        Returns
        -------
        utterances: list of Utterance
            List of utterances that occurred in this chat
        """
        return self._utterances

    @property
    def last_utterance(self):
        # type: () -> Utterance
        """
        Returns
        -------
        last_utterance: Utterance
            Most recent Utterance
        """
        return self._utterances[-1]

    def add_utterance(self, hypotheses, me):
        # type: (List[UtteranceHypothesis], bool) -> Utterance
        """
        Add Utterance to Conversation

        Parameters
        ----------
        hypotheses: list of UtteranceHypothesis

        Returns
        -------
        utterance: Utterance
        """
        utterance = Utterance(self, hypotheses, me, len(self._utterances))
        self._utterances.append(utterance)

        self._log = self._update_logger()
        self._log.info(utterance)

        return utterance

    def _update_logger(self):
        return logger.getChild("Chat {:19s} {:03d}".format("({})".format(self.speaker), len(self._utterances)))

    def __repr__(self):
        return "\n".join([str(utterance) for utterance in self._utterances])


class Utterance(object):

    def __init__(self, chat, hypotheses, me, turn):
        # type: (Chat, List[UtteranceHypothesis], bool, int) -> Utterance
        """
        Construct Utterance Object

        Parameters
        ----------
        chat: Chat
            Reference to Chat Utterance is part of
        hypotheses: List[UtteranceHypothesis]
            Hypotheses on uttered text (transcript, confidence)
        me: bool
            True if Robot spoke, False if Person Spoke
        turn: int
            Utterance Turn
        """

        self._log = logger.getChild(self.__class__.__name__)

        self._datetime = datetime.now()
        self._chat = chat
        self._turn = turn
        self._me = me

        self._hypothesis = self._choose_hypothesis(hypotheses)

        self._tokens = self._clean(self._tokenize(self.transcript))

        self._parser = None if self.me else Parser(self)

    @property
    def chat(self):
        # type: () -> Chat
        """
        Returns
        -------
        chat: Chat
            Utterance Chat
        """
        return self._chat

    @property
    def context(self):
        """
        Returns
        -------
        context: Context
            Utterance Context
        """
        return self.chat.context

    @property
    def type(self):
        # type: () -> UtteranceType
        raise NotImplementedError()

    @property
    def transcript(self):
        # type: () -> str
        """
        Returns
        -------
        transcript: str
            Utterance Transcript
        """
        return self._hypothesis.transcript

    @property
    def confidence(self):
        # type: () -> float
        """
        Returns
        -------
        confidence: float
            Utterance Confidence
        """
        return self._hypothesis.confidence

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
    def parser(self):
        # type: () -> Optional[Parser]
        """
        Returns
        -------
        parsed_tree: ntlk Tree generated by the CFG parser
        """
        return self._parser

    def _choose_hypothesis(self, hypotheses):
        return sorted(self._patch_names(hypotheses), key=lambda hypothesis: hypothesis.confidence, reverse=True)[0]

    def _patch_names(self, hypotheses):
        if not self.me:

            names = []

            # Patch Transcripts with Names
            for hypothesis in hypotheses:

                transcript = []

                for word in hypothesis.transcript.split():
                    name = Utterance._get_closest_name(word)

                    if name:
                        names.append(name)
                        transcript.append(name)
                    else:
                        transcript.append(word)

                hypothesis.transcript = " ".join(transcript)

            if names:
                # Count Name Frequency and Adjust Hypothesis Confidence
                names = Counter(names)
                max_freq = max(names.values())

                for hypothesis in hypotheses:
                    for name in names.keys():
                        if name in hypothesis.transcript:
                            hypothesis.confidence *= float(names[name]) / float(max_freq)

        return hypotheses

    @staticmethod
    def _get_closest_name(word, names=config.PEOPLE_FRIENDS_NAMES, max_name_distance=2):
        # type: (str, List[str], int) -> str
        if word[0].isupper():
            name, distance = sorted([(name, edit_distance(name, word)) for name in names], key=lambda key: key[1])[0]

            if distance <= max_name_distance:
                return name

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

        tokens_raw = transcript.replace("'", " ").split() # TODO possessive
        dict = {'m': 'am', 're': 'are', 'll': 'will', 's': 'is'}
        for key in dict:
            if key in tokens_raw:
                index = tokens_raw.index(key)
                tokens_raw.remove(key)
                tokens_raw.insert(index, dict[key])

        if 't' in tokens_raw:
            index = tokens_raw.index('t')
            tokens_raw.remove('t')
            tokens_raw.insert(index, 'not')

            if 'won' in tokens_raw:
                index = tokens_raw.index('won')
                tokens_raw.remove('won')
                tokens_raw.insert(index, 'will')

            if 'don' in tokens_raw:
                index = tokens_raw.index('don')
                tokens_raw.remove('don')
                tokens_raw.insert(index, 'do')

            if 'doesn' in tokens_raw:
                index = tokens_raw.index('doesn')
                tokens_raw.remove('doesn')
                tokens_raw.insert(index, 'does')

        '''
        tokens = []
        for word in tokens_raw:
            clean_word = re.sub('[!?]', '', word)
            tokens.append(clean_word)
        '''

        return tokens_raw

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
        return tokens

    def __repr__(self):
        author = config.NAME if self.me else self.chat.speaker
        return '{:>10s}: "{}"'.format(author, self.transcript)


class Parser(object):

    POS_TAGGER = None  # Type: POS
    CFG_GRAMMAR_FILE = os.path.join(os.path.dirname(__file__), 'data', 'cfg.txt')

    def __init__(self, utterance):

        if not Parser.POS_TAGGER:
            Parser.POS_TAGGER = POS()

        with open(Parser.CFG_GRAMMAR_FILE) as cfg_file:
            self._cfg = cfg_file.read()

        self._log = logger.getChild(self.__class__.__name__)

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
        self._log.debug(pos)

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
                pos[ind] = (w, 'VB')
            ind+=1

        if pos[0][0]=='Does':
            pos[0] = ('Does', 'VBD')

        ind = 0
        for word, tag in pos:
            if '?' in word:
                word=word[:-1]
                print(word)
            if tag.endswith('$'):
                new_rule = tag[:-1] + 'POS -> \'' + word + '\'\n'
                pos[ind] = (pos[ind][0], 'PRPPOS')

            else:
                new_rule = tag + ' -> \'' + word + '\'\n'
            if new_rule not in self._cfg:
                self._cfg += new_rule

            ind+=1

        try:
            cfg_parser = CFG.fromstring(self._cfg)
            RD = RecursiveDescentParser(cfg_parser)

            last_token = tokenized_sentence[len(tokenized_sentence)-1]

            if '?' in last_token:
                tokenized_sentence[len(tokenized_sentence)-1] = last_token[:-1]

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
                                s_r[index] = {'label': node.label()}
                                raw = ''
                                if len(node.leaves())>1:
                                    s_r[index]['structure']= branch
                                    for n in node.leaves():
                                        raw+=n+' '
                                    # deeper structure
                                else:
                                    raw = node.leaves()

                                s_r[index]['raw'] = raw
                            index+=1

            else:
                print('no forest')
                print(pos)

            for el in s_r:
                #print(el, s_r[el])
                if type(s_r[el]['raw']) == list:
                    string = ''
                    for e in s_r[el]['raw']:
                        string += e + ' '
                    s_r[el]['raw'] = string
                s_r[el]['raw'] = s_r[el]['raw'].strip()

            return forest, s_r

        except:
            return [], {}