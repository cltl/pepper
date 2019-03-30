from datetime import datetime
from typing import List, Optional


class RDFBase(object):
    def __init__(self, id, label, offset=None, confidence=0.0):
        # type: (str, str, Optional[slice], float) -> Entity
        """
        Construct RDFBase Object
        Parameters
        ----------
        id: str
            URI of RDFBase
        label: str
            Label of RDFBase
        offset: Optional[slice]
            Indeces of substring where this RDFBase was mentioned
        confidence: float
            Confidence value that this RDFBase was mentioned
        """

        self._id = id
        self._label = label
        self._offset = offset
        self._confidence = confidence

    @property
    def id(self):
        # type: () -> str
        return self._id

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
    def __init__(self, id, label, types, offset=None, confidence=0.0):
        # type: (str, str, List[str], Optional[slice], float) -> Entity
        """
        Construct Entity Object
        Parameters
        ----------
        id: str
            URI of entity
        label: str
            Label of entity
        types: List[str]
            List of types for this entity
        offset: Optional[slice]
            Indeces of substring where this entity was mentioned
        confidence: float
            Confidence value that this entity was mentioned
        """
        super(Entity, self).__init__(id, label, offset, confidence)

        self._types = types

    @property
    def types(self):
        # type: () -> List[str]
        return self._types
    
    
class Predicate(RDFBase):
    def __init__(self, id, label, offset=None, confidence=0.0, cardinality=1):
        # type: (str, str, Optional[slice], float, int) -> Entity
        """
        Construct Predicate Object
        Parameters
        ----------
        id: str
            URI of predicate
        label: str
            Label of predicate
        offset: Optional[slice]
            Indeces of substring where this predicate was mentioned
        confidence: float
            Confidence value that this predicate was mentioned
        cardinality: int
            Represents relation of predicate (Range cardinality)
        """
        super(Predicate, self).__init__(id, label, offset, confidence)

        self._cardinality = cardinality

    @property
    def cardinality(self):
        # type: () -> int
        return self._cardinality


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


class Provenance(object):
    def __init__(self, author, date):
        # type: (str, datetime) -> Provenance
        """
        Construct Provenance Object
        Parameters
        ----------
        author: str
            Person who said the mention
        date: datetime
            Date when the mention was said
        """

        self._author = author
        self._date = date

    @property
    def author(self):
        # type: () -> str
        return self._author

    @property
    def date(self):
        # type: () -> datetime
        return self._date


class CardinalityConflict(object):
    def __init__(self, provenance, entity):
        # type: (Provenance, Entity) -> CardinalityConflict
        """
        Construct CardinalityConflict Object
        Parameters
        ----------
        provenance: Provenance
            Information about who said the conflicting information and when
        entity: Entity
            Information about what the conflicting information is about
        """
        self._provenance = provenance
        self._object = entity

    @property
    def provenance(self):
        # type: () -> Provenance
        return self._provenance

    @property
    def object(self):
        # type: () -> Entity
        return self._object

    @property
    def author(self):
        # type: () -> str
        return self._provenance.author

    @property
    def date(self):
        # type: () -> datetime
        return self._provenance.date

    @property
    def object_name(self):
        # type: () -> str
        return self._object.label


class NegationConflict(object):
    def __init__(self, provenance, predicate):
        # type: (Provenance, Predicate) -> NegationConflict
        """
        Construct CardinalityConflict Object
        Parameters
        ----------
        provenance: Provenance
            Information about who said the conflicting information and when
        predicate: Predicate
            Information about what the conflicting information is about
        """
        self._provenance = provenance
        self._predicate = predicate

    @property
    def provenance(self):
        # type: () -> Provenance
        return self._provenance

    @property
    def predicate(self):
        # type: () -> Predicate
        return self._predicate

    @property
    def author(self):
        # type: () -> str
        return self._provenance.author

    @property
    def date(self):
        # type: () -> datetime
        return self._provenance.date

    @property
    def predicate_name(self):
        # type: () -> str
        return self._predicate.label


# TODO revise overlap with provenance
class StatementNovelty(object):
    def __init__(self, provenance):
        # type: (Provenance) -> StatementNovelty
        """
        Construct StatementNovelty Object
        Parameters
        ----------
        provenance: Provenance
            Information about who said the acquired information and when
        """
        self._provenance = provenance

    @property
    def provenance(self):
        # type: () -> Provenance
        return self._provenance

    @property
    def author(self):
        # type: () -> str
        return self._provenance.author

    @property
    def date(self):
        # type: () -> datetime
        return self._provenance.date


class EntityNovelty(object):
    def __init__(self, existance_subject, existance_object):
        # type: (bool, bool) -> EntityNovelty
        """
        Construct EntityNovelty Object
        Parameters
        ----------
        provenance: Provenance
            Information about who said the acquired information and when
        """
        self._subject = not existance_subject
        self._object = not existance_object

    @property
    def subject(self):
        # type: () -> bool
        return self._subject

    @property
    def object(self):
        # type: () -> bool
        return self._object


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

    def negation_conflicts(self):
        # type: () -> Optional[List[NegationConflict]]
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
