from datetime import date
from random import choice, sample, randint, uniform

from pepper.brain import RdfBuilder
from pepper.framework import UtteranceHypothesis, Context, Face
from pepper.framework.sensor.obj import Object
from pepper.language import Chat, Utterance, UtteranceType

places = ['Office']
friends = ['Piek', 'Lenka', 'Bram', 'Suzana', 'Selene', 'Lea', 'Thomas', 'Jaap', 'Tae']
binary_values = [True, False]

capsule_knows = {
    "utterance": "dimitris knows piek",
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

capsule_is_from = {
    "utterance": "bram is from mongolia",
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

capsule_is_from_2 = {
    "utterance": "bram is from mongolia",
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

capsule_is_from_3 = {
    "utterance": "bram is from mongolia",
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


def fake_objects(context):
    # Office
    if choice(binary_values) and context.location.label == 'Office':
        objects = [Object('person', 0.79, None, None), Object('laptop', 0.88, None, None),
                   Object('chair', 0.88, None, None), Object('laptop', 0.51, None, None),
                   Object('bottle', 0.88, None, None)]
    elif choice(binary_values) and context.location.label == 'Office':
        objects = [Object('person', 0.79, None, None), Object('plant', 0.88, None, None),
                   Object('chair', 0.88, None, None), Object('laptop', 0.51, None, None)]
    elif choice(binary_values) and context.location.label == 'Office':
        objects = [Object('person', 0.79, None, None), Object('plant', 0.88, None, None),
                   Object('chair', 0.88, None, None), Object('laptop', 0.51, None, None),
                   Object('book', 0.88, None, None), Object('laptop', 0.51, None, None)]

    # Market
    elif choice(binary_values) and context.location.label == 'Market':
        objects = [Object('apple', 0.79, None, None), Object('banana', 0.88, None, None),
                   Object('avocado', 0.51, None, None), Object('banana', 0.88, None, None)]
    elif choice(binary_values) and context.location.label == 'Market':
        objects = [Object('apple', 0.79, None, None), Object('banana', 0.88, None, None),
                   Object('avocado', 0.51, None, None), Object('strawberry', 0.88, None, None)]

    # Playground
    elif choice(binary_values) and context.location.label == 'Playground':
        objects = [Object('person', 0.79, None, None), Object('teddy bear', 0.88, None, None),
                   Object('teddy bear', 0.88, None, None), Object('cat', 0.51, None, None)]
    elif choice(binary_values) and context.location.label == 'Playground':
        objects = [Object('apple', 0.79, None, None), Object('banana', 0.88, None, None),
                   Object('cat', 0.51, None, None), Object('banana', 0.88, None, None)]

    # Other
    else:
        if context.location.label != 'Market':
            objects = [Object('teddy bear', 0.79, None, None), Object('dog', 0.88, None, None),
                       Object('cat', 0.51, None, None), Object('dog', 0.88, None, None)]
        else:
            objects = [Object('apple', 0.79, None, None), Object('banana', 0.88, None, None),
                       Object('avocado', 0.51, None, None), Object('strawberry', 0.88, None, None)]

    return objects


def fake_people():
    num_people = randint(0, len(friends))
    people = sample(friends, num_people)

    faces = set()
    for peep in people:
        confidence = uniform(0, 1)
        f = Face(peep, confidence, None, None, None)
        faces.add(f)

    # Add strangers?
    if choice(binary_values):
        confidence = uniform(0, 1)
        faces.add(Face('Stranger', confidence, None, None, None))

    return faces


def fake_context(empty=False, no_people=False, place=False):
    context = Context()

    # Set place
    if place:
        context.location._label = choice(places)

    faces = fake_people()
    objects = fake_objects(context)

    # Set objects
    if not empty:
        context.add_objects(objects)
        context.add_people(faces)

    if not no_people:
        context.add_objects(objects)

    return context


def fake_chat(capsule, context):
    chat = Chat(capsule['author'], context)
    chat.set_id(capsule['chat'])

    return chat


def fake_utterance(capsule, chat):
    hyp = UtteranceHypothesis(capsule['utterance'], 0.99)

    utt = Utterance(chat, [hyp], False, capsule['turn'])
    utt._type = UtteranceType.STATEMENT
    utt.set_turn(capsule['turn'])

    return utt


def fake_triple(capsule, utt):
    builder = RdfBuilder()

    triple = builder.fill_triple(capsule['subject'], capsule['predicate'], capsule['object'])
    utt.set_triple(triple)

    utt.pack_perspective(capsule['perspective'])


def transform_capsule(capsule, empty=False, no_people=False, place=False):
    context = fake_context(empty=empty, no_people=no_people, place=place)
    context.set_datetime(capsule['date'])

    chat = fake_chat(capsule, context)
    utt = fake_utterance(capsule, chat)

    fake_triple(capsule, utt)

    return utt
