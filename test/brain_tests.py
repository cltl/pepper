import json
from datetime import date

from pepper.brain.long_term_memory import LongTermMemory
from pepper.brain.utils.base_cases import statements, questions, experiences, visuals, sample_coco


if __name__ == "__main__":
    # Create brain connection
    brain = LongTermMemory()

    # Re import base
    # for stat in statements:
    #     brain.update(stat)
    #
    # brain.experience(experiences[0])

    # type = brain.keyword_match_dbpedia('Apple')
    #
    # capsule = {  # Leolani saw an apple
    #     "subject": {
    #         "label": "",
    #         "type": ""
    #     },
    #     "predicate": {
    #         "type": ""
    #     },
    #     "object": {
    #         "label": "apple",
    #         "type": type
    #     },
    #     "author": "front_camera",
    #     "chat": None,
    #     "turn": None,
    #     "position": "0-15-0-15",
    #     "date": date.today()
    # }
    #
    # brain.experience(capsule)
    # print(brain.get_classes())
    #

    # yes = 0
    # no = 0
    #
    # for item in sample_coco:
    #     x = brain.process_visual(item)
    #     if x is None:
    #         no = no + 1
    #     else:
    #         yes = yes + 1
    #
    # print('yes: {}\t no: {}'.format(yes, no))

    yes = 0
    no = 0

    for item in sample_coco:
        x = brain.process_visual(item, exact_only=False)
        if x is None:
            no = no + 1
        else:
            yes = yes + 1

    print('yes: {}\t no: {}'.format(yes, no))



