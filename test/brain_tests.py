import json

from pepper.brain.long_term_memory import LongTermMemory
from pepper.brain.utils.base_cases import statements, questions, experiences, visuals


if __name__ == "__main__":
    # Create brain connection
    brain = LongTermMemory()

    # Rebuild
    # brain._rebuild_brain_base()

    # print(json.dumps(brain.get_all_conflicts(), indent=4, sort_keys=False))
    # print(phrase_conflicts(brain.get_all_conflicts()))

    # print(json.dumps(brain.get_type_description('tv'), indent=4, sort_keys=False))
    # for visual in VISUALS:
    #     for item in visual:
    #         brain.process_visual(item)

    for statement in statements:
        response = brain.update(statement)