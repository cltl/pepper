from datetime import datetime

from typing import List, Optional


class RDFBase(object):
    @property
    def label(self):
        # type: () -> str
        raise NotImplementedError()

    @property
    def confidence(self):
        # type: () -> float
        raise NotImplementedError()

    @property
    def offset(self):
        # type: () -> slice
        raise NotImplementedError()


class Entity(RDFBase):
    @property
    def id(self):
        # type: () -> str
        raise NotImplementedError()

    @property
    def type(self):
        # type: () -> str
        raise NotImplementedError()
    
    
class Predicate(RDFBase):
    @property
    def cardinality(self):
        # type: () -> int
        raise NotImplementedError()


class Triple(object):
    @property
    def subject(self):
        # type: () -> Entity
        raise NotImplementedError()

    @property
    def predicate(self):
        # type: () -> Predicate
        raise NotImplementedError()

    @property
    def object(self):
        # type: () -> Entity
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


class Thoughts(object):
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
