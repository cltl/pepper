import json

from pepper.brain.long_term_memory import LongTermMemory
from pepper.brain.utils.base_cases import statements, questions, experiences, visuals


if __name__ == "__main__":
    # Create brain connection
    brain = LongTermMemory()

    # Re import base
    for stat in statements:
        brain.update(stat)

    brain.experience(experiences[0])

    brain.process_visual('fruit')
    brain.process_visual('chair')
    brain.process_visual('Red')


