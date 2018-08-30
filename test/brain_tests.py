import json
from datetime import date

from pepper.brain.long_term_memory import LongTermMemory
from pepper.brain.utils.base_cases import statements, questions, experiences, visuals


if __name__ == "__main__":
    # Create brain connection
    brain = LongTermMemory()

    # Re import base
    # for stat in statements:
    #     brain.update(stat)
    #
    # brain.experience(experiences[0])

    type = brain.process_visual('Apple')

    capsule = {  # Leolani saw an apple
        "subject": {
            "label": "",
            "type": ""
        },
        "predicate": {
            "type": ""
        },
        "object": {
            "label": "apple",
            "type": type
        },
        "author": "front_camera",
        "chat": None,
        "turn": None,
        "position": "0-15-0-15",
        "date": date.today()
    }

    brain.experience(capsule)
    print(brain.get_classes())

    brain.process_visual('chair')
    brain.process_visual('Red')


