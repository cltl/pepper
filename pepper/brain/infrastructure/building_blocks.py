import random
from rdflib import Literal
from datetime import date, datetime
from typing import List, Optional

from nltk.stem import WordNetLemmatizer

from pepper.brain.utils.constants import NOT_TO_MENTION_TYPES
from pepper.brain.utils.helper_functions import hash_claim_id, is_proper_noun


class RDFBase(object):
    def __init__(self, id, label, offset=None, confidence=0.0):
        # type: (str, str, Optional[slice], float) -> None
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
        # type: (str, str, List[str], Optional[slice], float) -> None
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
        self._types = list(dict.fromkeys(self._types))

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
        # type: (str, str, Optional[slice], float, int) -> None
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

    def casefold(self, subject, complement, format='triple'):
        # type (str) -> ()
        """
        Format the labels to match triples or natural language
        Parameters
        ----------
        format

        Returns
        -------

        """

        subject_label = subject.label if subject is not None and subject.label not in ['', Literal('')] else (
            subject.types if subject is not None else '?')
        complement_label = complement.label if complement is not None and complement.label not in ['', Literal('')] else (
            complement.types if complement is not None else '?')

        if format == 'triple':
            # Label
            self._label = Literal(self.label.lower().replace(" ", "-"))
            self._label = Literal(
                self._fix_predicate_morphology(subject_label, str(self.label), complement_label, format=format))

        elif format == 'natural':
            # Label
            self._label = self.label.lower().replace("-", " ")
            self._label = self._fix_predicate_morphology(subject_label, self.label, complement_label, format=format)

    @staticmethod
    def _fix_predicate_morphology(subject, predicate, complement, format='triple'):
        """
        Conjugation
        Parameters
        ----------
        subject
        predicate

        Returns
        -------

        """
        # TODO: Copied from language.utils.helper_functions, because of circular dependency issues...
        # TODO revise by Lenka
        new_predicate = ''
        if format == 'triple':
            if len(predicate.split()) > 1:
                for el in predicate.split():
                    if el == 'is':
                        new_predicate += 'be-'
                    else:
                        new_predicate += el + '-'

            elif predicate.endswith('s'):
                new_predicate = WordNetLemmatizer().lemmatize(predicate)

            else:
                new_predicate = predicate

        elif format == 'natural':
            if len(predicate.split()) > 1:
                for el in predicate.split():
                    if el == 'be':
                        new_predicate += 'is '
                    else:
                        new_predicate += el + ' '

            # elif predicate == wnl.lemmatize(predicate):
            #    new_predicate = predicate + 's'

            else:
                new_predicate = predicate

        return new_predicate.strip(' ')


class Triple(object):
    def __init__(self, subject, predicate, complement):
        # type: (Entity, Predicate, Entity) -> None
        """
        Construct Triple Object
        Parameters
        ----------
        subject: Entity
            Instance that is the subject of the information just received
        predicate: Predicate
            Predicate of the information just received
        complement: Entity
            Instance that is the complement of the information just received
        """

        self._subject = subject
        self._predicate = predicate
        self._complement = complement

    @property
    def subject(self):
        # type: () -> Entity
        return self._subject

    @property
    def predicate(self):
        # type: () -> Predicate
        return self._predicate

    @property
    def complement(self):
        # type: () -> Entity
        return self._complement

    @property
    def subject_name(self):
        # type: () -> str
        return self._subject.label if self._subject is not None else None

    @property
    def predicate_name(self):
        # type: () -> str
        return self._predicate.label if self._predicate is not None else None

    @property
    def complement_name(self):
        # type: () -> str
        return self._complement.label if self._complement is not None else None

    @property
    def subject_types(self):
        # type: () -> str
        return self._subject.types_names if self._subject is not None else None

    @property
    def complement_types(self):
        # type: () -> str
        return self._complement.types_names if self._complement is not None else None

    # TODO not good practice and not used, might think of deleting three setters below
    def set_subject(self, subject):
        # type: (Entity) -> ()
        self._subject = subject

    def set_predicate(self, predicate):
        # type: (Predicate) -> ()
        self._predicate = predicate

    def set_complement(self, complement):
        # type: (Entity) -> ()
        self._complement = complement

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
        self._complement.casefold(format)
        self._predicate.casefold(self.subject, self.complement, format)

    def __iter__(self):
        return iter([('subject', self.subject), ('predicate', self.predicate), ('complement', self.complement)])

    def __repr__(self):
        return '{} [{}])'.format(hash_claim_id([self.subject_name
                                                if self.subject_name is not None
                                                   and self.subject_name not in ['', Literal('')] else '?',
                                                self.predicate_name
                                                if self.predicate_name is not None
                                                   and self.predicate_name not in ['', Literal('')] else '?',
                                                self.complement_name
                                                if self.complement_name is not None
                                                   and self.complement_name not in ['', Literal('')] else '?']),
                                 hash_claim_id([self.subject_types if self.subject_types is not None else '?',
                                                '->',
                                                self.complement_types if self.complement_types is not None else '?']))


class Perspective(object):
    def __init__(self, certainty, polarity, sentiment, time=None, emotion=None):
        # type: (float, int, float, Time, Emotion) -> None
        """
        Construct Perspective Object
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


class Provenance(object):
    def __init__(self, author, date):
        # type: (str, date) -> None
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
        # type: (Provenance, Entity) -> None
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
        self._complement = entity

    @property
    def provenance(self):
        # type: () -> Provenance
        return self._provenance

    @property
    def complement(self):
        # type: () -> Entity
        return self._complement

    @property
    def author(self):
        # type: () -> str
        return self._provenance.author

    @property
    def date(self):
        # type: () -> date
        return self._provenance.date

    @property
    def complement_name(self):
        # type: () -> str
        return self._complement.label

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
        self._complement.casefold(format)

    def __repr__(self):
        return '{} about {}'.format(self._provenance.__repr__(), self.complement_name)


class NegationConflict(object):
    def __init__(self, provenance, polarity_value):
        # type: (Provenance, polarity_value) -> None
        """
        Construct CardinalityConflict Object
        Parameters
        ----------
        provenance: Provenance
            Information about who said the conflicting information and when
        polarity_value: str
            Information about polarity of the statement
        """
        self._provenance = provenance
        self._polarity_value = polarity_value

    @property
    def provenance(self):
        # type: () -> Provenance
        return self._provenance

    @property
    def polarity_value(self):
        # type: () -> str
        return self._polarity_value

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

        # TODO: Cannot Casefold String, uncommented for now?
        # self._polarity_value.casefold(format)

    def __repr__(self):
        return '{} about {}'.format(self._provenance.__repr__(), self.polarity_value)


# TODO revise overlap with provenance
class StatementNovelty(object):
    def __init__(self, provenance):
        # type: (Provenance) -> None
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
    def __init__(self, existence_subject, existence_complement):
        # type: (bool, bool) -> None
        """
        Construct EntityNovelty Object
        Parameters
        ----------
        existence_subject: bool
            Truth value for determining if this subject is something new
        existence_complement: bool
            Truth value for determining if this complement is something new
        """
        self._subject = not existence_subject
        self._complement = not existence_complement

    @property
    def subject(self):
        # type: () -> bool
        return self._subject

    @property
    def complement(self):
        # type: () -> bool
        return self._complement

    def __repr__(self):
        return '{} - {}'.format(self.subject, self.complement)


class Gap(object):
    def __init__(self, predicate, entity):
        # type: (Predicate, Entity) -> None
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
        self._entity.casefold(format)
        self._predicate.casefold(self.entity, None, format)

    def __repr__(self):
        return '{} {}'.format(self.predicate_name, self.entity_range_name)


class Gaps(object):
    def __init__(self, subject_gaps, complement_gaps):
        # type: (List[Gap], List[Gap]) -> None
        """
        Construct Gap Object
        Parameters
        ----------
        subject_gaps: List[Gap]
            List of gaps with potential things to learn about the original subject
        complement_gaps: List[Gap]
            List of gaps with potential things to learn about the original complement
        """
        self._subject = subject_gaps
        self._complement = complement_gaps

    @property
    def subject(self):
        # type: () -> List[Gap]
        return self._subject

    @property
    def complement(self):
        # type: () -> List[Gap]
        return self._complement

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
        for g in self._complement:
            g.casefold(format)

    def __repr__(self):
        s = random.choice(self._subject) if self._subject else ''
        o = random.choice(self._complement) if self._complement else ''
        return '{} - {}'.format(s.__repr__(), o.__repr__())


class Overlap(object):
    def __init__(self, provenance, entity):
        # type: (Provenance, Entity) -> None
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
    def __init__(self, subject_overlaps, complement_overlaps):
        # type: (List[Overlap], List[Overlap]) -> None
        """
        Construct Overlap Object
        Parameters
        ----------
        subject_overlaps: List[Overlap]
            List of overlaps shared with original subject
        complement_overlaps: List[Overlap]
            List of overlaps shared with original complement
        """
        self._subject = subject_overlaps
        self._complement = complement_overlaps

    @property
    def subject(self):
        # type: () -> List[Overlap]
        return self._subject

    @property
    def complement(self):
        # type: () -> List[Overlap]
        return self._complement

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
        for g in self._complement:
            g.casefold(format)

    def __repr__(self):
        s = random.choice(self._subject) if self._subject else ''
        o = random.choice(self._complement) if self._complement else ''
        return '{} - {}'.format(s.__repr__(), o.__repr__())


class Thoughts(object):
    def __init__(self, statement_novelty, entity_novelty, negation_conflicts, complement_conflict,
                 subject_gaps, complement_gaps, overlaps, trust):
        # type: (List[StatementNovelty], EntityNovelty, List[NegationConflict], List[CardinalityConflict], Gaps, Gaps, Overlaps, float) -> None
        """
        Construct Thoughts Object
        Parameters
        ----------
        statement_novelty: List[StatementNovelty]
            Information if the statement is novel
        entity_novelty: EntityNovelty
            Information if the entities involved are novel
        negation_conflicts: Optional[List[NegationConflict]]
            Information regarding conflicts of opposing statements heard
        complement_conflict: List[CardinalityConflict]
            Information regarding conflicts by violating one to one predicates
        subject_gaps: Gaps
            Information about what can be learned of the subject
        complement_gaps_gaps: Gaps
            Information about what can be learned of the complement
        overlaps: Overlaps
            Information regarding overlaps of this statement with things heard so far
        trust: float
            Level of trust on this actor
        """

        self._statement_novelty = statement_novelty
        self._entity_novelty = entity_novelty
        self._negation_conflicts = negation_conflicts
        self._complement_conflict = complement_conflict
        self._subject_gaps = subject_gaps
        self._complement_gaps = complement_gaps
        self._overlaps = overlaps
        self._trust = trust

    def complement_conflicts(self):
        # type: () -> List[CardinalityConflict]
        return self._complement_conflict

    def negation_conflicts(self):
        # type: () -> List[NegationConflict]
        return self._negation_conflicts

    def statement_novelties(self):
        # type: () -> List[StatementNovelty]
        return self._statement_novelty

    def entity_novelty(self):
        # type: () -> EntityNovelty
        return self._entity_novelty

    def complement_gaps(self):
        # type: () -> Gaps
        return self._complement_gaps

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
        for c in self._complement_conflict:
            c.casefold(format)
        self._subject_gaps.casefold(format)
        self._complement_gaps.casefold(format)
        self._overlaps.casefold(format)

    def __repr__(self):
        representation = {'statement_novelty': self._statement_novelty, 'entity_novelty': self._entity_novelty,
                          'negation_conflicts': self._negation_conflicts,
                          'complement_conflict': self._complement_conflict,
                          'subject_gaps': self._subject_gaps, 'complement_gaps': self._complement_gaps,
                          'overlaps': self._overlaps}

        return '{}'.format(representation)
