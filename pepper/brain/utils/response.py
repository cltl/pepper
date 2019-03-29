from pepper.brain.utils.helper_functions import date_from_uri

from datetime import datetime
from typing import List, Optional


class RDFBase(object):
    def __init__(self, label, offset=None, confidence=0.0):
        # type: (str, Optional[slice], float) -> Entity
        """
        Construct Entity Object
        Parameters
        ----------
        response_item: dict
            Direct output from query representing a conflict on a one to one predicate
        """

        self._label = label
        self._offset = offset
        self._confidence = confidence

    @property
    def label(self):
        # type: () -> str
        return self._label

    @property
    def offset(self):
        # type: () -> Optional[slice]
        return self._offset

    @property
    def confidence(self):
        # type: () -> float
        return self._confidence


class Entity(RDFBase):
    def __init__(self, label, id, types, offset=None, confidence=0.0):
        # type: (str, str, List[str], Optional[slice], float) -> Entity
        """
        Construct Entity Object
        Parameters
        ----------
        response_item: dict
            Direct output from query representing a conflict on a one to one predicate
        """
        super(Entity, self).__init__(label, offset, confidence)

        self._id = id
        self._types = types

    @property
    def id(self):
        # type: () -> str
        return self._id

    @property
    def types(self):
        # type: () -> List[str]
        return self._types
    
    
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
    def __init__(self, response_item, entity):
        # type: (dict, Entity) -> CardinalityConflict
        """
        Construct CardinalityConflict Object
        Parameters
        ----------
        response_item: dict
            Direct output from query representing a conflict on a one to one predicate
        """
        self._author = response_item['authorlabel']['value']
        self._date = date_from_uri(response_item['date']['value'])
        self._object = entity

    @property
    def author(self):
        # type: () -> str
        return self._author

    @property
    def date(self):
        # type: () -> datetime
        return self._date

    @property
    def object(self):
        # type: () -> Entity
        return self._object


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


class Gap(object):
    @property
    def predicate(self):
        # type: () -> Predicate
        raise NotImplementedError()

    @property
    def entity(self):
        # type: () -> Entity
        raise NotImplementedError()


class Gaps(object):
    @property
    def object(self):
        # type: () -> List[Gap]
        raise NotImplementedError()

    @property
    def subject(self):
        # type: () -> List[Gap]
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
        # type: () -> Gaps
        raise NotImplementedError()

    def subject_gaps(self):
        # type: () -> Gaps
        raise NotImplementedError()

    def overlaps(self):
        # type: () -> Overlaps
        raise NotImplementedError()

    def trust(self):
        # type: () -> float
        raise NotImplementedError()
