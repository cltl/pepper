import random
from rdflib import Literal
from datetime import date, datetime
from typing import List, Optional

from pepper.brain.utils.constants import NOT_TO_MENTION_TYPES
from pepper.brain.utils.helper_functions import hash_claim_id, is_proper_noun


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
        if format == 'triple':
            # Label
            self._label = Literal(self.label.lower().replace(" ", "-"))

        elif format == 'natural':
            # Label
            self._label = self.label.lower().replace("-", " ")

    def __repr__(self):
        return '{}'.format(self.label)


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

        self._types = [t for t in types if t != '' and t is not None]

    @property
    def types(self):
        # type: () -> List[str]
        return self._types

    @property
    def types_names(self):
        # type: () -> str
        return ' or '.join([t for t in self._types if t.lower() not in NOT_TO_MENTION_TYPES])

    def add_types(self, types):
        # type: (List[str]) -> ()
        fixed_types = [t for t in types if t != '' and t is not None]
        self._types.extend(fixed_types)

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
        if format == 'triple':
            # Label
            self._label = Literal(self.label.lower().replace(" ", "-"))
            # Types
            self._types = [t.lower().replace(" ", "_") for t in self.types]

        elif format == 'natural':
            # Label
            self._label = self.label.lower().replace("_", " ")
            self._label = self._label.capitalize() if is_proper_noun(self.types) else self._label
            # Types
            self._types = [t.lower().replace("_", " ") for t in self.types]


class Predicate(RDFBase):
    def __init__(self, id, label, offset=None, confidence=0.0, cardinality=1):
        # type: (str, str, Optional[slice], float, int) -> Predicate
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
    def __init__(self, subject, predicate, object):
        # type: (Entity, Predicate, Entity) -> Triple
        """
        Construct Triple Object
        Parameters
        ----------
        subject: Entity
            Instance that is the subject of the information just received
        predicate: Predicate
            Predicate of the information just received
        object: Entity
            Instance that is the object of the information just received
        """

        self._subject = subject
        self._predicate = predicate
        self._object = object

    @property
    def subject(self):
        # type: () -> Entity
        return self._subject

    @property
    def predicate(self):
        # type: () -> Predicate
        return self._predicate

    @property
    def object(self):
        # type: () -> Entity
        return self._object

    @property
    def subject_name(self):
        # type: () -> str
        return self._subject.label if self._subject is not None else None

    @property
    def predicate_name(self):
        # type: () -> str
        return self._predicate.label if self._predicate is not None else None

    @property
    def object_name(self):
        # type: () -> str
        return self._object.label if self._object is not None else None

    # TODO not good practice and not used, might think of deleting three setters below
    def set_subject(self, subject):
        # type: (Entity) -> ()
        self._subject = subject

    def set_predicate(self, predicate):
        # type: (Predicate) -> ()
        self._predicate = predicate

    def set_object(self, object):
        # type: (Entity) -> ()
        self._object = object

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
        self._subject.casefold(format)
        self._predicate.casefold(format)
        self._object.casefold(format)

    def __iter__(self):
        return iter([('subject', self.subject), ('predicate', self.predicate), ('object', self.object)])

    def __repr__(self):
        return '{}'.format(hash_claim_id([self.subject_name
                                              if self.subject_name is not None
                                                 and self.subject_name not in ['', Literal('')] else '?',
                                          self.predicate_name
                                              if self.predicate_name is not None
                                                 and self.predicate_name not in ['', Literal('')] else '?',
                                          self.object_name
                                              if self.object_name is not None
                                                 and self.object_name not in ['', Literal('')] else '?']))


class Provenance(object):
    def __init__(self, author, date):
        # type: (str, date) -> Provenance
        """
        Construct Provenance Object
        Parameters
        ----------
        author: str
            Person who said the mention
        date: date
            Date when the mention was said
        """

        self._author = author
        self._date = datetime.strptime(date, '%Y-%m-%d')

    @property
    def author(self):
        # type: () -> str
        return self._author

    @property
    def date(self):
        # type: () -> date
        return self._date

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
        if format == 'triple':
            # Label
            self._author = self.author.lower().replace(" ", "_")

        elif format == 'natural':
            # Label
            self._author = self.author.lower().replace("_", " ")

    def __repr__(self):
        return '{} on {}'.format(self.author, self.date.strftime("%B,%Y"))


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
        # type: () -> date
        return self._provenance.date

    @property
    def object_name(self):
        # type: () -> str
        return self._object.label

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
        self._provenance.casefold(format)
        self._object.casefold(format)

    def __repr__(self):
        return '{} about {}'.format(self._provenance.__repr__(), self.object_name)


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
        # type: () -> date
        return self._provenance.date

    @property
    def predicate_name(self):
        # type: () -> str
        return self._predicate.label

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
        self._provenance.casefold(format)
        self._predicate.casefold(format)

    def __repr__(self):
        return '{} about {}'.format(self._provenance.__repr__(), self.predicate_name)


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
        # type: () -> date
        return self._provenance.date

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
        self._provenance.casefold(format)

    def __repr__(self):
        return '{}'.format(self._provenance.__repr__())


class EntityNovelty(object):
    def __init__(self, existence_subject, existence_object):
        # type: (bool, bool) -> EntityNovelty
        """
        Construct EntityNovelty Object
        Parameters
        ----------
        existence_subject: bool
            Truth value for determining if this subject is something new
        existence_object: bool
            Truth value for determining if this object is something new
        """
        self._subject = not existence_subject
        self._object = not existence_object

    @property
    def subject(self):
        # type: () -> bool
        return self._subject

    @property
    def object(self):
        # type: () -> bool
        return self._object

    def __repr__(self):
        return '{} - {}'.format(self.subject, self.object)


class Gap(object):
    def __init__(self, predicate, entity):
        # type: (Predicate, Entity) -> Gap
        """
        Construct Gap Object
        Parameters
        ----------
        predicate: Predicate
            Information about what can be known for the entity
        entity: Entity
            Information about the type of things that can be known
        """
        self._predicate = predicate
        self._entity = entity

    @property
    def predicate(self):
        # type: () -> Predicate
        return self._predicate

    @property
    def entity(self):
        # type: () -> Entity
        return self._entity

    @property
    def predicate_name(self):
        # type: () -> str
        return self._predicate.label

    @property
    def entity_range(self):
        # type: () -> List[str]
        return self._entity.types

    @property
    def entity_range_name(self):
        # type: () -> str
        return self._entity.types_names

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
        self._predicate.casefold(format)
        self._entity.casefold(format)

    def __repr__(self):
        return '{} {}'.format(self.predicate_name, self.entity_range_name)


class Gaps(object):
    def __init__(self, subject_gaps, object_gaps):
        # type: (List[Gap], List[Gap]) -> Gaps
        """
        Construct Gap Object
        Parameters
        ----------
        subject_gaps: List[Gap]
            List of gaps with potential things to learn about the original subject
        object_gaps: List[Gap]
            List of gaps with potential things to learn about the original object
        """
        self._subject = subject_gaps
        self._object = object_gaps

    @property
    def object(self):
        # type: () -> List[Gap]
        return self._subject

    @property
    def subject(self):
        # type: () -> List[Gap]
        return self._object

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
        for g in self._subject:
            g.casefold(format)
        for g in self._object:
            g.casefold(format)

    def __repr__(self):
        s = random.choice(self._subject) if self._subject else ''
        o = random.choice(self._object) if self._object else ''
        return '{} - {}'.format(s.__repr__(), o.__repr__())


class Overlap(object):
    def __init__(self, provenance, entity):
        # type: (Provenance, Entity) -> Overlap
        """
        Construct Overlap Object
        Parameters
        ----------
        provenance
        entity
        """
        self._provenance = provenance
        self._entity = entity

    @property
    def provenance(self):
        # type: () -> Provenance
        return self._provenance

    @property
    def entity(self):
        # type: () -> Entity
        return self._entity

    @property
    def author(self):
        # type: () -> str
        return self._provenance.author

    @property
    def date(self):
        # type: () -> date
        return self._provenance.date

    @property
    def entity_name(self):
        # type: () -> str
        return self._entity.label

    @property
    def entity_types(self):
        # type: () -> List[str]
        return self._entity.types

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
        self._provenance.casefold(format)
        self._entity.casefold(format)

    def __repr__(self):
        return '{} about {}'.format(self._provenance.__repr__(), self.entity_name)


class Overlaps(object):
    def __init__(self, subject_overlaps, object_overlaps):
        # type: (List[Overlap], List[Overlap]) -> Overlaps
        """
        Construct Overlap Object
        Parameters
        ----------
        subject_overlaps: List[Overlap]
            List of overlaps shared with original subject
        object_overlaps: List[Overlap]
            List of overlaps shared with original object
        """
        self._subject = subject_overlaps
        self._object = object_overlaps

    @property
    def subject(self):
        # type: () -> List[Overlap]
        return self._subject

    @property
    def object(self):
        # type: () -> List[Overlap]
        return self._object

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
        for g in self._subject:
            g.casefold(format)
        for g in self._object:
            g.casefold(format)

    def __repr__(self):
        s = random.choice(self._subject) if self._subject else ''
        o = random.choice(self._object) if self._object else ''
        return '{} - {}'.format(s.__repr__(), o.__repr__())


class Thoughts(object):
    def __init__(self, statement_novelty, entity_novelty, negation_conflicts, object_conflict,
                 subject_gaps, object_gaps, overlaps, trust):
        # type: (List[StatementNovelty], EntityNovelty, List[NegationConflict], List[CardinalityConflict], Gaps, Gaps, Overlaps, float) -> Thoughts
        """
        Construct Thoughts object
        Parameters
        ----------
        statement_novelty: List[StatementNovelty]
            Information if the statement is novel
        entity_novelty: EntityNovelty
            Information if the entities involved are novel
        negation_conflicts: Optional[List[NegationConflict]]
            Information regarding conflicts of opposing statements heard
        object_conflict: List[CardinalityConflict]
            Information regarding conflicts by violating one to one predicates
        subject_gaps: Gaps
            Information about what can be learned of the subject
        object_gaps: Gaps
            Information about what can be learned of the object
        overlaps: Overlaps
            Information regarding overlaps of this statement with things heard so far
        trust: float
            Level of trust on this actor
        """

        self._statement_novelty = statement_novelty
        self._entity_novelty = entity_novelty
        self._negation_conflicts = negation_conflicts
        self._object_conflict = object_conflict
        self._subject_gaps = subject_gaps
        self._object_gaps = object_gaps
        self._overlaps = overlaps
        self._trust = trust

    def object_conflict(self):
        # type: () -> List[CardinalityConflict]
        return self._object_conflict

    def negation_conflicts(self):
        # type: () -> List[NegationConflict]
        return self._negation_conflicts

    def statement_novelties(self):
        # type: () -> List[StatementNovelty]
        return self._statement_novelty

    def entity_novelty(self):
        # type: () -> EntityNovelty
        return self._entity_novelty

    def object_gaps(self):
        # type: () -> Gaps
        return self._object_gaps

    def subject_gaps(self):
        # type: () -> Gaps
        return self._subject_gaps

    def overlaps(self):
        # type: () -> Overlaps
        return self._overlaps

    def trust(self):
        # type: () -> float
        return self._trust

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
        for n in self._statement_novelty:
            n.casefold(format)
        for c in self._negation_conflicts:
            c.casefold(format)
        for c in self._object_conflict:
            c.casefold(format)
        self._subject_gaps.casefold(format)
        self._object_gaps.casefold(format)
        self._overlaps.casefold(format)

    def __repr__(self):
        representation = {'statement_novelty': self._statement_novelty, 'entity_novelty': self._entity_novelty,
                          'negation_conflicts': self._negation_conflicts, 'object_conflict': self._object_conflict,
                          'subject_gaps': self._subject_gaps, 'object_gaps': self._object_gaps,
                          'overlaps': self._overlaps}

        return '{}'.format(representation)
