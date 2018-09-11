import json
from datetime import date

from pepper.brain.long_term_memory import LongTermMemory
from pepper.brain.utils.base_cases import statements, questions, experiences, visuals, sample_coco


if __name__ == "__main__":
    # Create brain connection
    brain = LongTermMemory()

    # # Re import base
    # for stat in statements:
    #     brain.update(stat)
    #
    # # Reconstruct from logs 31 aug
    # with open('/Users/mytomorrows/Downloads/correct_info.txt', 'r') as f:
    #     x = f.readlines()
    #
    # x = set(x)
    #
    # for i in x:
    #     capsule = {  # Leolani saw an apple
    #         "subject": {
    #             "label": "",
    #             "type": ""
    #         },
    #         "predicate": {
    #             "type": ""
    #         },
    #         "object": {
    #             "label": "{}".format(i.strip()),
    #             "type": ''
    #         },
    #         "author": "front_camera",
    #         "chat": None,
    #         "turn": None,
    #         "position": "0-15-0-15",
    #         "date": date(2018,8,31)
    #     }
    #
    #     brain.experience(capsule)
    #
    # capsule = {  # bram likes romantic movies
    #     "subject": {
    #         "label": "bram",
    #         "type": "person"
    #     },
    #     "predicate": {
    #         "type": "likes"
    #     },
    #     "object": {
    #         "label": "romantic_movies",
    #         "type": "film_genre"
    #     },
    #     "author": "lenka",
    #     "chat": None,
    #     "turn": None,
    #     "position": "0-25",
    #     "date": date(2018,8,31)
    # }
    # brain.update(capsule)
    #
    # capsule = {  # bram likes romantic movies
    #     "subject": {
    #         "label": "bram",
    #         "type": "person"
    #     },
    #     "predicate": {
    #         "type": "likes"
    #     },
    #     "object": {
    #         "label": "science_fiction_movies",
    #         "type": "film_genre"
    #     },
    #     "author": "bram",
    #     "chat": None,
    #     "turn": None,
    #     "position": "0-25",
    #     "date": date(2018,8,31)
    # }
    #
    # brain.update(capsule)

    # Test dbpedia lookup
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

    # yes = 0
    # no = 0
    #
    # for item in sample_coco:
    #     x, y = brain.process_visual(item, exact_only=False)
    #     if x is None:
    #         no = no + 1
    #     else:
    #         yes = yes + 1
    #         print(y)
    #
    # print('yes: {}\t no: {}'.format(yes, no))



