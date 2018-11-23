from pepper.brain.long_term_memory import LongTermMemory
from pepper.brain.utils.helper_functions import phrase_all_conflicts, phrase_negation_conflicts

import json


# Create brain connection
brain = LongTermMemory()


capsule = {  # lenka saw a dog
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
        "author": None,
        "chat": None,
        "turn": None,
        "position": None,
        "date": None
    }

conflicts = brain.get_negation_conflicts_with_statement(capsule)

# print(json.dumps(conflicts, indent=4))

print(phrase_negation_conflicts(conflicts))


