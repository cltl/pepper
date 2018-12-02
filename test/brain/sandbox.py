from pepper.brain.long_term_memory import LongTermMemory
from pepper.brain.utils.helper_functions import phrase_all_conflicts, phrase_cardinality_conflicts, \
    phrase_negation_conflicts, phrase_statement_novelty, phrase_type_novelty, phrase_update

import json
from datetime import date


# Create brain connection
brain = LongTermMemory()


capsule_serbia = {  # lenka saw a dog
        "subject": {
            "label": "lenka",
            "type": ""
        },
        "predicate": {
            "type": "sees"
        },
        "object": {
            "label": "dog",
            "type": ""
        },
        "author": "selene",
        "chat": 1,
        "turn": 1,
        "position": "0-25",
        "date": date(2018, 3, 19)
    }

# capsule_serbia = {  # lenka is from Serbia
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

x = brain.update(capsule_serbia)
print(json.dumps(x, indent=4, sort_keys=True))
print(phrase_cardinality_conflicts(x['cardinality_conflicts'], capsule_serbia))
print(phrase_negation_conflicts(x['negation_conflicts'], capsule_serbia))
print(phrase_statement_novelty(x['statement_novelty']))
print(phrase_type_novelty(x['entity_novelty'], capsule_serbia))


print('\n\n')
print(phrase_update(x))





