from pepper.language.generation.phrasing import phrase_update
from pepper.brain import LongTermMemory, RdfBuilder
from pepper.language import Chat, Utterance
from pepper.framework import UtteranceHypothesis

from datetime import date


def transform_capsule(capsule, context=None):
    """
    Build proper Utterance object from capsule. Step required for proper refactoring
    Parameters
    ----------
    capsule
    context

    Returns
    -------

    """
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

capsule_serbia = {  # lenka saw a dog
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
        "author": "selene",
        "chat": 1,
        "turn": 1,
        "position": "0-25",
        "date": date(2018, 3, 19)
    }

# capsule_serbia = {  # bram is from mongolia
#         "subject": {
#             "label": "bram",
#             "type": "person"
#         },
#         "predicate": {
#             "type": "is_from"
#         },
#         "object": {
#             "label": "mongolia",
#             "type": "location"
#         },
#         "author": "selene",
#         "chat": 1,
#         "turn": 1,
#         "position": "0-25",
#         "date": date(2018, 3, 19)
#     }

# capsule_serbia = { # human likes pizza
#     u'predicate': {u'type': u'like'},
#     u'chat': 490254330820530247757705225416035124L,
#     u'author': u'Human',
#     u'object': {u'type': u'', u'id': u'', u'label': u'pizza'},
#     u'turn': 6,
#     u'utterance_type': 'STATEMENT',
#     u'date': date(2019, 3, 29), u'position': u'',
#     u'response': {u'role': u'', u'format': u''},
#     u'subject': {u'type': u'', u'id': u'', u'label': u'human'}}

capsule_serbia = transform_capsule(capsule_serbia)

x = brain.update(capsule_serbia)
print(phrase_update(x, True, True))
