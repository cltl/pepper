import json

from pepper.brain.long_term_memory import LongTermMemory
from pepper.brain.utils.base_cases import statements, questions, experiences, visuals


if __name__ == "__main__":
    # Create brain connection
    brain = LongTermMemory()

    # # Rebuild
    # for statement in statements:
    #     response = brain.update(statement)

    for visual in experiences:
        for item in visual:
            brain.process_visual(item)
