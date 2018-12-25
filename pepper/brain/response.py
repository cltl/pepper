from enum import Enum
from datetime import datetime

from typing import List, Optional


class UtteranceType(Enum):
    STATEMENT = 0
    QUESTION = 1
    EXPERIENCE = 2


class Certainty(Enum):
    CERTAIN = 0
    PROBABLE = 1
    POSSIBLE = 2
    UNDERSPECIFIED = 3


class Sentiment(Enum):
    NEGATIVE = 0
    POSITIVE = 1


class Emotion(Enum):
    ANGER = 0
    DISGUST = 1
    FEAR = 2
    HAPPINESS = 3
    SADNESS = 4
    SURPRISE = 5


class RDFBase(object):
    @property
    def type(self):
        # type: () -> str
        raise NotImplementedError()

    @property
    def confidence(self):
        # type: () -> float
        raise NotImplementedError()

    @property
    def position(self):
        # type: () -> str
        raise NotImplementedError()


class Entity(RDFBase):
    @property
    def id(self):
        # type: () -> str
        raise NotImplementedError()
    
    @property
    def label(self):
        # type: () -> str
        raise NotImplementedError()
    
    
class Predicate(RDFBase):
    @property
    def cardinality(self):
        # type: () -> int
        raise NotImplementedError()


class Statement(object):
    @property
    def object(self):
        # type: () -> Entity
        raise NotImplementedError()

    @property
    def subject(self):
        # type: () -> Entity
        raise NotImplementedError()

    @property
    def predicate(self):
        # type: () -> Predicate
        raise NotImplementedError()


class CardinalityConflict(object):
    @property
    def author(self):
        # type: () -> str
        raise NotImplementedError()

    @property
    def date(self):
        # type: () -> datetime
        raise NotImplementedError()

    @property
    def object(self):
        # type: () -> Entity
        raise NotImplementedError()


class NegationConflict(object):
    @property
    def author(self):
        # type: () -> str
        raise NotImplementedError()

    @property
    def date(self):
        # type: () -> datetime
        raise NotImplementedError()

    @property
    def predicate(self):
        # type: () -> Predicate
        raise NotImplementedError()


class StatementNovelty(object):
    @property
    def author(self):
        # type: () -> str
        raise NotImplementedError()

    @property
    def date(self):
        # type: () -> datetime
        raise NotImplementedError()


class EntityNovelty(object):
    @property
    def object(self):
        # type: () -> bool
        raise NotImplementedError()

    @property
    def subject(self):
        # type: () -> bool
        raise NotImplementedError()


class BrainGap(object):
    @property
    def predicate(self):
        # type: () -> Predicate
        raise NotImplementedError()

    @property
    def entity(self):
        # type: () -> Entity
        raise NotImplementedError()


class BrainGaps(object):
    @property
    def object(self):
        # type: () -> List[BrainGap]
        raise NotImplementedError()

    @property
    def subject(self):
        # type: () -> List[BrainGap]
        raise NotImplementedError()


class Overlap(object):
    @property
    def author(self):
        # type: () -> str
        raise NotImplementedError()

    @property
    def date(self):
        # type: () -> datetime
        raise NotImplementedError()

    @property
    def entity(self):
        # type: () -> Entity
        raise NotImplementedError()


class Overlaps(object):
    @property
    def object(self):
        # type: () -> List[Overlap]
        raise NotImplementedError()

    @property
    def subject(self):
        # type: () -> List[Overlap]
        raise NotImplementedError()


# TODO: Merge with language.Utterance
class MetaIn(object):
    @property
    def raw(self):
        # type: () -> str
        raise NotImplementedError()

    @property
    def type(self):
        # type: () -> UtteranceType
        raise NotImplementedError()

    @property
    def author(self):
        # type: () -> str
        raise NotImplementedError()

    @property
    def chat(self):
        # type: () -> int
        raise NotImplementedError()

    @property
    def turn(self):
        # type: () -> int
        raise NotImplementedError()

    @property
    def date(self):
        # type: () -> datetime
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


class MetaOut(object):
    def cardinality_conflicts(self):
        # type: () -> List[CardinalityConflict]
        raise NotImplementedError()

    def negation_conflict(self):
        # type: () -> Optional[NegationConflict]
        raise NotImplementedError()

    def statement_novelties(self):
        # type: () -> List[StatementNovelty]
        raise NotImplementedError()

    def entity_novelty(self):
        # type: () -> EntityNovelty
        raise NotImplementedError()

    def object_gaps(self):
        # type: () -> BrainGaps
        raise NotImplementedError()

    def subject_gaps(self):
        # type: () -> BrainGaps
        raise NotImplementedError()

    def overlaps(self):
        # type: () -> Overlaps
        raise NotImplementedError()

    def trust(self):
        # type: () -> float
        raise NotImplementedError()


class BrainResponse(object):
    @property
    def statement(self):
        # type: () -> Statement
        raise NotImplementedError()

    @property
    def meta_in(self):
        # type: () -> MetaIn
        raise NotImplementedError()

    @property
    def meta_out(self):
        # type: () -> MetaOut
        raise NotImplementedError()
