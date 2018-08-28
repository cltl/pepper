import json

from pepper.brain.long_term_memory import LongTermMemory
from pepper.brain.utils.base_cases import statements, questions, experiences, visuals


if __name__ == "__main__":
    # Create brain connection
    brain = LongTermMemory()

    # brain.update(statements[0])

    # brain.experience(experiences[0])

    brain.get_last_chat_id()


