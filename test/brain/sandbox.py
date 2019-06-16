from pepper.language.generation.thoughts_phrasing import phrase_thoughts
from pepper.brain import LongTermMemory, RdfBuilder
from pepper.language import Chat, Utterance, UtteranceType
from pepper.framework import UtteranceHypothesis, Context, Face
from pepper.framework.sensor.obj import Object

from datetime import date
from random import choice

places = ['Office', 'Classroom']  # , 'Forest', 'Playground', 'Monastery', 'House', 'University', 'Hotel']


def fake_context(empty=False, no_people=False, place=False):
    bl = [True, False]

    if choice(bl):
        objects = {Object('person', 0.79, None, None), Object('teddy bear', 0.88, None, None),
                   Object('dog', 0.88, None, None), Object('cat', 0.51, None, None)}
    elif choice(bl):
        objects = {Object('person', 0.79, None, None), Object('teddy bear', 0.88, None, None),
                   Object('teddy bear', 0.88, None, None), Object('cat', 0.51, None, None)}
    else:
        objects = {Object('apple', 0.79, None, None), Object('banana', 0.88, None, None),
                   Object('cat', 0.51, None, None), Object('banana', 0.88, None, None)}

    faces = {Face('Selene', 0.90, None, None, None), Face('Stranger', 0.90, None, None, None)}

    context = Context()
    if not empty:
        context.add_objects(objects)
        context.add_people(faces)

    if not no_people:
        context.add_objects(objects)

    if place:
        context.location._label = choice(places)

    return context


def transform_capsule(capsule, empty=False, no_people=False, place=False):
    """
    Build proper Utterance object from capsule. Step required for proper refactoring
    Parameters
    ----------
    capsule
    context

    Returns
    -------

    """
    context = fake_context(empty=empty, no_people=no_people, place=place)

    chat = Chat(capsule['author'], context)
    hyp = UtteranceHypothesis('this is a test', 0.99)

    utt = Utterance(chat, [hyp], False, capsule['turn'])
    utt._type = UtteranceType.STATEMENT

    builder = RdfBuilder()

    triple = builder.fill_triple(capsule['subject'], capsule['predicate'], capsule['object'])

    utt.set_triple(triple)

    return utt


# Create brain connection
brain = LongTermMemory(clear_all=True)

conlficts = brain.get_all_conflicts()

capsule_knows = {  # dimitris knows piek
    "subject": {
        "label": "karla",
        "type": "person"
    },
    "predicate": {
        "type": "live-in"
    },
    "object": {
        "label": "paris",
        "type": "location"
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

capsules = [capsule_likes, capsule_is_from, capsule_is_from_2, capsule_is_from_3, capsule_knows, capsule_likes,
            capsule_likes, capsule_is_from, capsule_is_from_2, capsule_is_from_3, capsule_knows, capsule_likes]
bl = [True, False]

for capsule in capsules:
    say = ''
    em = choice(bl)
    np = choice(bl)
    p = choice(bl)
    capsule = transform_capsule(capsule, empty=em, no_people=np, place=p)
    x = brain.update(capsule, reason_types=True)

    if capsule.context.location.label == capsule.context.location.UNKNOWN:
        y = brain.reason_location(capsule.context)
        if y is None:
            z = choice(places)
            brain.set_location_label(z)
            capsule.context.location._label = z
            say += 'Having a talk at what I will call %s' % capsule.context.location.label
        else:
            brain.set_location_label(y)
            capsule.context.location._label = y
            say += 'Having a talk at what I figure out is %s' % capsule.context.location.label

    else:
        say += 'Having a talk at %s' % capsule.context.location.label
    print(say)

    # print(phrase_thoughts(x, True, True))
    # print(phrase_thoughts(x, True, True))
    # print(phrase_thoughts(x, True, True))
    # print(phrase_thoughts(x, True, True))
    # print(phrase_thoughts(x, True, True))
    # print(phrase_thoughts(x, True, True))
    # print(phrase_thoughts(x, True, True))
    # print(phrase_thoughts(x, True, True))
    # print(phrase_thoughts(x, True, True))
    # print(phrase_thoughts(x, True, True))
    # print(phrase_thoughts(x, True, True))
    # print(phrase_thoughts(x, True, True))
    # print(phrase_thoughts(x, True, True))
    # print(phrase_thoughts(x, True, True))
    # print(phrase_thoughts(x, True, True))
    # print(phrase_thoughts(x, True, True))
    # print(phrase_thoughts(x, True, True))
    # print(phrase_thoughts(x, True, True))
    # print(phrase_thoughts(x, True, True))
    # print(phrase_thoughts(x, True, True))
    # print(phrase_thoughts(x, True, True))

# for x in range(10):
#     say = ''
#     emn = choice(bl)
#     npn = choice(bl)
#     context = fake_context(empty=emn, no_people=npn)
#     say += 'Compared with context b: %s,%s\n' % (emn, npn)
#
#     y = brain.reason_location(context)
#     if y is None:
#         z = choice(places)
#         # brain.set_location_label(z)
#         context.location._label = z
#         say += 'I did not know where I was, but I will call it %s' % context.location.label
#     else:
#         # brain.set_location_label(y)
#         context.location._label = y
#         say += 'I assume I am at %s' % context.location.label
#
#     print(say)
