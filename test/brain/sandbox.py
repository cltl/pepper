from pepper.brain.long_term_memory import LongTermMemory
from pepper.brain.utils.base_cases import statements


# Create brain connection
brain = LongTermMemory()

# Re import base
for stat in statements:
    brain.update(stat)