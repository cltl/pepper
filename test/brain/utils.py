from pepper.brain import RdfBuilder
from pepper.language import Chat, Utterance, UtteranceType
from pepper.framework import UtteranceHypothesis, Context, Face
from pepper.framework.sensor.obj import Object

from datetime import date
from random import choice

places = ['Forest', 'Playground', 'Monastery', 'House', 'University', 'Hotel', 'Office']

signal = False
bl = [True, False]

capsule_knows = {  # dimitris knows piek
    "subject": {
        "label": "dimitris",
        "type": "person"
    },
    "predicate": {
        "type": "knows"
    },
    "object": {
        "label": "piek",
        "type": "person"
    },
    "author": "tom",
    "turn": 1,
    "position": "0-25",
    "date": date(2019, 1, 24)
}

capsule_is_from = {  # bram is from mongolia
    "subject": {
        "label": "bram",
        "type": "person"
    },
    "predicate": {
        "type": "be-from"
    },
    "object": {
        "label": "netherlands",
        "type": "location"
    },
    "author": "bram",
    "chat": 1,
    "turn": 1,
    "position": "0-25",
    "date": date(2018, 3, 19)
}

capsule_is_from_2 = {  # bram is from mongolia
    "subject": {
        "label": "bram",
        "type": "person"
    },
    "predicate": {
        "type": "be-from"
    },
    "object": {
        "label": "mongolia",
        "type": "location"
    },
    "author": "lenka",
    "chat": 1,
    "turn": 1,
    "position": "0-25",
    "date": date(2018, 3, 25)
}

capsule_is_from_3 = {  # bram is from mongolia
    "subject": {
        "label": "piek",
        "type": "person"
    },
    "predicate": {
        "type": "be-from"
    },
    "object": {
        "label": "netherlands",
        "type": "location"
    },
    "author": "bram",
    "chat": 1,
    "turn": 1,
    "position": "0-25",
    "date": date(2018, 3, 25)
}

capsule_likes = {  # human likes pizza
    u'predicate': {u'type': u'like'},
    u'chat': 490254330820530247757705225416035124L,
    u'author': u'Human',
    u'object': {u'type': u'', u'id': u'', u'label': u'pizza'},
    u'turn': 6,
    u'utterance_type': 'STATEMENT',
    u'date': date(2019, 3, 29), u'position': u'',
    u'response': {u'role': u'', u'format': u''},
    u'subject': {u'type': u'', u'id': u'', u'label': u'human'}}


def fake_context(empty=False, no_people=False, place=False):
    if choice(bl):
        faces = {Face('Selene', 0.90, None, None, None), Face('Stranger', 0.90, None, None, None)}
    else:
        faces = {Face('Selene', 0.90, None, None, None), Face('Piek', 0.90, None, None, None)}

    context = Context()
    if place:
        context.location._label = choice(places)

    if choice(bl) and not signal and context.location.label == 'Office':
        objects = [Object('person', 0.79, None, None), Object('laptop', 0.88, None, None),
                   Object('chair', 0.88, None, None), Object('laptop', 0.51, None, None),
                   Object('teddy bear', 0.88, None, None)]
    elif choice(bl) and not signal and context.location.label == 'Office':
        objects = [Object('person', 0.79, None, None), Object('plant', 0.88, None, None),
                   Object('chair', 0.88, None, None), Object('laptop', 0.51, None, None)]
    elif choice(bl) and not signal and context.location.label == 'Market':
        objects = [Object('apple', 0.79, None, None), Object('banana', 0.88, None, None),
                   Object('avocado', 0.51, None, None), Object('banana', 0.88, None, None)]
    elif choice(bl) and not signal and context.location.label == 'Market':
        objects = [Object('apple', 0.79, None, None), Object('banana', 0.88, None, None),
                   Object('avocado', 0.51, None, None), Object('strawberry', 0.88, None, None)]
    elif choice(bl) and not signal and context.location.label == 'Playground':
        objects = [Object('person', 0.79, None, None), Object('teddy bear', 0.88, None, None),
                   Object('teddy bear', 0.88, None, None), Object('cat', 0.51, None, None)]
    elif choice(bl) and not signal and context.location.label == 'Playground':
        objects = [Object('apple', 0.79, None, None), Object('banana', 0.88, None, None),
                   Object('cat', 0.51, None, None), Object('banana', 0.88, None, None)]
        # signal = True
    else:
        if context.location.label != 'Market':
            objects = [Object('teddy bear', 0.79, None, None), Object('dog', 0.88, None, None),
                       Object('cat', 0.51, None, None), Object('dog', 0.88, None, None)]
        else:
            objects = [Object('apple', 0.79, None, None), Object('banana', 0.88, None, None),
                       Object('avocado', 0.51, None, None), Object('strawberry', 0.88, None, None)]

    if not empty:
        context.add_objects(objects)
        context.add_people(faces)

    if not no_people:
        context.add_objects(objects)

    return context


def transform_capsule(capsule, empty=False, no_people=False, place=False):
    context = fake_context(empty=empty, no_people=no_people, place=place)

    chat = Chat(capsule['author'], context)
    hyp = UtteranceHypothesis('this is a test', 0.99)

    utt = Utterance(chat, [hyp], False, capsule['turn'])
    utt._type = UtteranceType.STATEMENT

    builder = RdfBuilder()

    triple = builder.fill_triple(capsule['subject'], capsule['predicate'], capsule['object'])
    utt.set_triple(triple)

    perspective = {'sentiment': 0, 'certainty': 1, 'polarity': 1}
    utt.pack_perspective(perspective)

    return utt
