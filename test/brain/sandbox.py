from pepper.language.generation.thoughts_phrasing import phrase_thoughts
from pepper.brain import LongTermMemory, RdfBuilder
from pepper.language import Chat, Utterance
from pepper.framework import UtteranceHypothesis, Context, Object, Face

from datetime import date


def transform_capsule(capsule):
    """
    Build proper Utterance object from capsule. Step required for proper refactoring
    Parameters
    ----------
    capsule
    context

    Returns
    -------

    """
    objects = {Object('person', 0.79, None, None), Object('teddy bear', 0.88, None, None), Object('cat', 0.51, None, None)}
    faces = {Face('Selene', 0.90, None, None, None), Face('Stranger', 0.90, None, None, None)}

    context = Context()
    context.add_objects(objects)
    context.add_people(faces)

    chat = Chat(capsule['author'], context)
    hyp = UtteranceHypothesis('this is a test', 0.99)

    utt = Utterance(chat, [hyp], False, capsule['turn'])

    builder = RdfBuilder()

    triple = builder.fill_triple(capsule['subject'], capsule['predicate'], capsule['object'])

    utt.set_triple(triple)

    return utt


# Create brain connection
brain = LongTermMemory()

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
            "label": "mongolia",
            "type": "location"
        },
        "author": "bram",
        "chat": 1,
        "turn": 1,
        "position": "0-25",
        "date": date(2018, 3, 19)
    }

capsule_likes = { # human likes pizza
    u'predicate': {u'type': u'like'},
    u'chat': 490254330820530247757705225416035124L,
    u'author': u'Human',
    u'object': {u'type': u'', u'id': u'', u'label': u'pizza'},
    u'turn': 6,
    u'utterance_type': 'STATEMENT',
    u'date': date(2019, 3, 29), u'position': u'',
    u'response': {u'role': u'', u'format': u''},
    u'subject': {u'type': u'', u'id': u'', u'label': u'human'}}

capsules = [capsule_knows, capsule_is_from, capsule_likes]

for capsule in capsules:
    capsule = transform_capsule(capsule)

    x = brain.update(capsule)
    break
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
