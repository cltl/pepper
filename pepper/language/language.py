from __future__ import unicode_literals

from pepper.language.pos import POS
from pepper.language.analyzer import Analyzer
from pepper.language.utils.atoms import UtteranceType
from pepper.language.utils.helper_functions import names, check_rdf_completeness

from pepper.brain.utils.helper_functions import casefold_text
from pepper.brain.utils.rdf_builder import RdfBuilder
from pepper.brain.utils.response import Triple

from pepper import logger, config

from nltk import CFG, RecursiveDescentParser, edit_distance

from collections import Counter

from random import getrandbits
from datetime import datetime
import enum
import os

from typing import List, Optional


class Time(enum.Enum):
    PAST = -1
    PRESENT = 0
    FUTURE = 1


class Emotion(enum.Enum):  # Not used yet
    ANGER = 0
    DISGUST = 1
    FEAR = 2
    HAPPINESS = 3
    SADNESS = 4
    SURPRISE = 5


class Perspective(object):
    def __init__(self, certainty, polarity, sentiment, time=None, emotion=None):
        # type: (float, int, float, Time, Emotion) -> Perspective
        """
        Construct Perspective object
        Parameters
        ----------
        certainty: float
            Float between 0 and 1. 1 is the default value and things reflecting doubt affect it to make it less certain
        polarity: int
            Either 1 for positive polarity or -1 for negative polarity. This value directly affects the sentiment
        sentiment: float
            Float between -1 and 1. Negative values represent negatuve sentiments while positive values represent
            positive sentiments.
        time: Time
            Enumerator representing time. This is extracted from the tense
        emotion: Emotion
            Enumerator representing one of the 6 universal emotions.
        """
        self._certainty = certainty
        self._polarity = polarity
        self._sentiment = sentiment
        self._time = time
        self._emotion = emotion

    @property
    def certainty(self):
        # type: () -> float
        return self._certainty

    @property
    def polarity(self):
        # type: () -> int
        return self._polarity

    @property
    def sentiment(self):
        # type: () -> float
        return self._sentiment

    @property
    def time(self):
        # type: () -> Optional[Time]
        return self._time

    @property
    def emotion(self):
        # type: () -> Optional[Emotion]
        return self._emotion


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
        # analyze sets triple, perspective and type
        self._type = 'Statement'  # UtteranceType.STATEMENT # TODO do not keep this hard coded

        # TODO Check this with Bram, currently we initialize with None and have set methods
        self._triple = None
        self._perspective = None

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
    def chat_speaker(self):
        # type: () -> str
        """
        Returns
        -------
        speaker: str
            Name of speaker (a.k.a. the person Pepper has a chat with)
        """
        return self._chat.speaker

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
        """
        Returns
        -------
        type: UtteranceType
            Whether the utterance was a statement, a question or an experience
        """
        return self._type

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
        """
        Returns
        -------
        triple: Triple
            Structured representation of the utterance
        """
        return self._triple

    @property
    def perspective(self):
        # type: () -> Perspective
        """
        Returns
        -------
        perspective: Perspective
            NLP features related to the utterance
        """
        return self._perspective

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

    def analyze(self):
        """
        Determines the type of utterance, extracts the RDF triple and perspective attaching them to the last utterance
        Parameters
        ----------
        chat

        Returns
        -------

        """
        analyzer = Analyzer.analyze(self._chat)

        if not analyzer:
            return "I cannot parse your input"

        Analyzer.LOG.debug("RDF {}".format(analyzer.rdf))

        if analyzer.utterance_type == UtteranceType.STATEMENT:
            if not check_rdf_completeness(analyzer.rdf):
                # TODO intransitive verbs
                Analyzer.LOG.debug('incomplete statement RDF')
                return

        self.write_template(analyzer.rdf, analyzer.utterance_type)

        '''
        if analyzer.utterance_type == UtteranceType.STATEMENT:
            perspective = analyzer.perspective
            print(perspective)
            for el in perspective:
                if el!='fix':
                    template[el] = perspective[el]
        '''

    def write_template(self, rdf, utterance_type):
        """
        Sets utterance type, the extracted triple and (in future) the perspective
        Parameters
        ----------
        rdf
        utterance_type

        Returns
        -------

        """
        self._type = utterance_type  # TODO make a setter?
        if type(rdf) == str:
            return rdf

        if not rdf:
            return 'error in the rdf'

        builder = RdfBuilder()

        # Build subject
        subject = builder.fill_entity(casefold_text(rdf['subject'], format='triple'), ["person"])  # capitalization

        # Build predicate
        if rdf['predicate'] == 'seen':
            predicate = builder.fill_predicate('sees')
            # template['object']['hack'] = True  # TODO what does this mean?
        else:
            predicate = builder.fill_predicate(casefold_text(rdf['predicate'], format='triple'))

        # Build object
        if rdf['object'] in names:
            object = builder.fill_entity(casefold_text(rdf['object'], format='triple'), ["person"])

        elif type(rdf['object']) is list:
            if rdf['object'][0] and rdf['object'][0].strip() in ['a', 'an', 'the']:
                rdf['object'].remove(rdf['object'][0])

            if len(rdf['object']) > 1:
                object = builder.fill_entity(casefold_text(rdf['object'][0], format='triple'),
                                             casefold_text(rdf['object'][1], format='triple'))
            else:
                object = builder.fill_entity_from_label(casefold_text(rdf['object'][0], format='triple'))

        else:
            if rdf['object'].lower().startswith('a '):
                rdf['object'] = rdf['object'][2:]
            object = builder.fill_entity_from_label(casefold_text(rdf['object'], format='triple'))

        self.set_triple(Triple(subject, predicate, object))
        # new things in template: certainty , sentiment, types of NE, mention indexes

    # TODO check this with Bram
    def set_triple(self, triple):
        # type: (Triple) -> ()
        self._triple = triple

    def set_perspective(self, perspective):
        # type: (Perspective) -> ()
        self._perspective = perspective

    def casefold(self, format='triple'):
        # type (str) -> ()
        """
        Format the labels to match triples or natural language
        Parameters
        ----------
        format

        Returns
        -------

        """
        self._triple.casefold(format)

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
